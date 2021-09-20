;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; CALL CONVENTIOIN
;   R0 - R3 arg or variable
;  R4, R5 RETURN
;   R6,R7 countdown
;   A is always temp
;   the callee should store and recovery the R2-R5
; 
; This file provides IAP function and allows you 
; to program ROM via UART. This function should be
; called explicitly at startup:
;           CALL 0xFF00
;
; And for this program, if we wait too long for
; no data comes from host, we will return to the user
; program. to determine a proper tick,  we provide a small
; piece code named TEST_WAIT_UART. to get expected tick:
;   - modify the TEST_WAIT_UART_EXPECT_US to time that
;           you want to wait(in us)
;   - use the simulator(tools/Digital.exe) to load the 
;        src/circuit/TOP_IAP_test.dig and this program
;   - run the program until the CPU be halted
;   - get the R6, R7, the expected count will be
;       (0xFFFF - R7 << 8 + R6)
;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;; set this flag to enable the function to get the
;; count of timeout( coressponding to the expect time you want
;; to want                                                                             
TEST_WAIT_UART_FLAG EQU 0
TEST_WAIT_UART_EXPECT_US EQU 6000
 
;-----------------------------------------------------------

;PSW     DATA    D0H
;ACC     DATA    E0H
;B       DATA    F0H
;SP      DATA    81H
;DPL     DATA    82H
;DPH     DATA    83H
;SCON    DATA    98H
;SBUF    DATA    99H
TUARTL  DATA    9AH
TUARTH  DATA    9BH

DBGR    DATA    0xFF
DBGPAR1 DATA    0xFE
DBGPAR0 DATA    0xFD
    
DBGR_HALT_PROGRAM   EQU 0x04
DBGR_START_TIMMER   EQU 0x05

; RI     BIT     98H
; REN    BIT     9CH


LOAD_C16 MACRO   L, H, num
    MOV L, #LOW(num)
    MOV H, #(num SHR 8)
    ENDM

LOAD_TIMER MACRO TL, TH, tick
    LOAD_C16 TL, TH,  (0xFFFF - tick + 1)
    ENDM
    
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;
;;;;;         START of the program
;;;;;
CSEG AT 0x0000
MOV SP, #7

IF TEST_WAIT_UART_FLAG <> 0
    CLR 0x20.0
    LOAD_C16 DBGPAR0, DBGPAR1, TEST_WAIT_UART_EXPECT_US
    MOV     DBGR, #DBGR_START_TIMMER
    CALL    TEST_WAIT_UART_INIT
ELSE
    CALL 0xFF00
ENDIF


MOV DBGR, #DBGR_HALT_PROGRAM
JMP $

TEST_WAIT_UART_INIT:
    LOAD_C16 R6,R7, 0xFFFF
    JMP TEST_WAIT_UART
    
TEST_WAIT_UART:
JNB     P3.0, TEST_WAIT_UART_COUNTDOWN
MOV     R5, SBUF
CLR     P3.0
RET

TEST_WAIT_UART_COUNTDOWN:
;; COUNT_DONW -= -1
MOV     A, R6
ORL     A, R7
JZ      TEST_WAIT_UART_TIMEOUT


MOV     A, R6
DEC     R6
JNZ     TEST_WAIT_UART

DEC     R7
JMP     TEST_WAIT_UART

TEST_WAIT_UART_TIMEOUT:
RET


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;
;;;;;           IAP
;;;;;
CSEG AT 0xFF00
JMP START_ISP

;-----------------------------------------------------------

SEQ_HANDSHAKE:      DB 0xFF,0xA5,0x5A,0xCC
SEQ_HANDSHAKE_LEN  EQU $ - SEQ_HANDSHAKE
HANDSHAKE_TOLERABLE_MISMATCH EQU 100 ;; when handshaking, how many unexpected responses that you can tolerate


INTERNAL_MICRO_PSW_FLAG_MATCH   EQU 0xAB
    
USR_CMD_INTERNAL_MICRO_PROGRAM  EQU 0
USR_CMD_READ_BLOCK              EQU 3
USR_CMD_READ_ECHO               EQU 4
    
;; when we wait the data of SBUF, we will use a R6,R7 as 
;; a 16 bit counter,as the counter count down to 0,
;; we will deem such case as timeout so that we go to 
;; user program directly wait 
WAIT_HANDSHAKE_MAX_COUNT EQU 5000 ; for comman case . around 10ms
WAIT_SHORT_MAX_COUNT EQU 10000 ; for comman case . around 10ms
;; when the host didn't enable SDP accidently, we will use this
;; to trgger
;;       countdown, size, data0,addr0   , data1,addr1   , data2,addr2  ,   
SEQ_SDP: DB 0x88, 0x13,  0x3, 0xaa,0x55,0x55, 0x55,0xaa,0x2a, 0xa0,0x55,0x55
SEQ_SDP_SIZE            EQU $ - SEQ_SDP
SEQ_SDP_RAM_START_ADDR  EQU 0x1B
SEQ_SDP_OPCODE          EQU 1    
;-----------------------------------------------------------

START_ISP:
;; ----------- INITAL UART
; set timmer of uart, max baud rate of 62500 at 1 Mhz of CPU clock

LOAD_TIMER TUARTL,TUARTH, 1
;enable receiving
SETB REN 

;; ------------- HAND SHAKE WITH host
; try hank shake with host, the host should send a sequence of number
; that same as SEQ_HANDSHAKE


MOV  DPTR,   #SEQ_HANDSHAKE
CLR A
MOV PSW, A
MOV R0,  A
MOV R1,  #HANDSHAKE_TOLERABLE_MISMATCH

; handshake
;; check if the code that I received is consistent with the number in SEQ HANDSHAKE
HAND_SHAKE_NEXT:
MOV A, R1
JNZ     HAND_SHAKE_RETRY
JMP     EXIT_PROGRAM

HAND_SHAKE_RETRY:
ACALL READ_UART_WAIT_HANDSHAKE
MOV  A, R0
MOVC A, @A+DPTR
XRL  A, R5
DEC  R1
JNZ HAND_SHAKE_NEXT
;; to tell the host that I received the correct number,
;; send back its One's complement
MOV A, R5
CPL A
JNB TI, $
MOV SBUF, A
CLR TI
;; reset countdown after succes
; verify next number
INC R0
MOV R1,  #HANDSHAKE_TOLERABLE_MISMATCH
CJNE R0, #SEQ_HANDSHAKE_LEN, HAND_SHAKE_NEXT



;;;;;;; ----------- user commands
USER_COMMANDS:
ACALL READ_UART_WAIT_LONG
; cmd code in R3
MOV  A, R5
MOV  R3, A
CJNE A, #USR_CMD_INTERNAL_MICRO_PROGRAM, OP_NEXT2


    ;;  0 -- call internal ROM's micro_program
    ; get size, store in 0x17
    ACALL READ_UART_WAIT_SHORT  ;;; get PSW.1
    CLR PSW.1
    CJNE R5, #INTERNAL_MICRO_PSW_FLAG_MATCH,  CALL_INTERNAL_MICRO_PROGRAM_GET_A
    SETB PSW.1

    CALL_INTERNAL_MICRO_PROGRAM_GET_A:
    ACALL READ_UART_WAIT_SHORT ;;; get A, but need to be stored at first
    MOV R3, 5
    ACALL READ_UART_WAIT_SHORT ;;; get B
    MOV B, R5
    ACALL READ_UART_WAIT_SHORT ;;; get start address of data
    MOV R1, 5
    ACALL READ_UART_WAIT_SHORT ;;; get size of data
    MOV R0, 5

    LOAD_DATA_ARRAY:
        ACALL READ_UART_WAIT_SHORT
        MOV @R1, 5
        INC R1
        DJNZ R0, LOAD_DATA_ARRAY
        
    MOV A, R3
    DB  0xA5
    CLR PSW.1
    
    ;; give feedback to host
    JNB TI, $
    MOV A, R3
    CPL A
    MOV SBUF, A
    JMP    USER_COMMANDS 



OP_NEXT2: 
    CJNE A, #USR_CMD_READ_BLOCK, OP_NEXT3
    ; 3 -- read block
    ACALL READ_UART_WAIT_SHORT
    MOV DPL,R5
    ACALL READ_UART_WAIT_SHORT
    MOV DPH,R5
    ACALL READ_UART_WAIT_SHORT
    MOV R4,5
    ACALL READ_UART_WAIT_SHORT
    ;; MOV R5,R5
    READ_NEXT_BYTE_FROM_ROM:
        MOV     A, R4
        ORL     A, R5
        JZ      USER_COMMANDS
        CLR     A
        MOVC     A, @A+DPTR
        JNB     TI, $
        MOV     SBUF, A
        
        INC     DPTR
        MOV     A, R4
        DEC     R4
        JNZ     READ_NEXT_BYTE_FROM_ROM

        DEC     R5
        JMP     READ_NEXT_BYTE_FROM_ROM


OP_NEXT3:
    CJNE A, #USR_CMD_READ_ECHO, OP_NEXT4
    ;; 4 -- just echo
    ; load length
    ACALL READ_UART_WAIT_SHORT
    JNB TI, $
    MOV SBUF, R5
    JMP USER_COMMANDS

OP_NEXT4:
    JMP    EXIT_PROGRAM


    

READ_UART_WAIT_SHORT:
    LOAD_C16 R6,R7, WAIT_SHORT_MAX_COUNT
    JMP READ_UART

READ_UART_WAIT_LONG EQU READ_UART_WAIT_SHORT

READ_UART_WAIT_HANDSHAKE:
    LOAD_C16 R6,R7, WAIT_HANDSHAKE_MAX_COUNT
    JMP READ_UART



READ_UART:
    WAIT_UART_UNTIL_TIMEOUT:
        ; COUNTDOWN = WAIT_HANDSHAKE_MAX_COUNT;
        JNB     RI, READ_UART_COUNTDOWN
        MOV     R5, SBUF
        CLR     RI
        RET

    READ_UART_COUNTDOWN:
        ;; COUNT_DONW -= -1
        MOV     A, R6
        ORL     A, R7
        JZ      EXIT_PROGRAM_FROM_READ_UART


        MOV     A, R6
        DEC     R6
        JNZ     WAIT_UART_UNTIL_TIMEOUT

        DEC     R7
        JMP     WAIT_UART_UNTIL_TIMEOUT


EXIT_PROGRAM_FROM_READ_UART:
    ;; need to blance the stack
    POP ACC
    POP ACC
EXIT_PROGRAM:
;;; enable SDP automatically
    MOV R0,     #SEQ_SDP_RAM_START_ADDR
    MOV R1,     #SEQ_SDP_SIZE
    MOV DPTR,   #SEQ_SDP
    AUTO_DISABLE_SDP:
        CLR  A
        MOVC A, @A+DPTR
        MOV	@R0, A
        INC DPTR
        INC R0
        DJNZ    R1, AUTO_DISABLE_SDP

    CLR A
    MOV  A, #(0xFF - SEQ_SDP_OPCODE)
    MOV  B, A
    CPL  A
    SETB PSW.1
    DB 0xA5
        
;; Clear SBUF
    CLR  REN
    EXIT_PROGRAMCLR_RI:
        CLR  RI
        JB   RI, EXIT_PROGRAMCLR_RI
        
    CLR A
    MOV B, A
    MOV DPL, A
    MOV DPH, A
    MOV PSW, A
    RET
END