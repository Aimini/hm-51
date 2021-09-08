;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; CALL CONVENTIOIN
;   R1 - R3 arg or variable
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

;; when we wait the data of SBUF, we will use a R6,R7 as 
;; a 16 bit counter,as the counter count down to 0,
;; we will deem such case as timeout so that we go to 
;; user program directly wait 
WAIT_SHORT_MAX_COUNT EQU 16 ; for comman case . around 1ms
WAIT_LONG_MAX_COUNT  EQU 85 ;for CMD    .around 6ms

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

HAND_SHAKE_INITIALIING:
CLR A
MOV PSW, A
MOV R0,  A

HAND_SHAKE_NEXT:
; handshake
;; check if the code that I received is consistent with the number in SEQ HANDSHAKE


LCALL READ_UART_WAIT_SHORT
MOV  A, R0
MOVC A, @A+DPTR
XRL  A, R5
JNZ HAND_SHAKE_INITIALIING
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
CJNE R0, #SEQ_HANDSHAKE_LEN, HAND_SHAKE_NEXT

;;;;;;; ----------- user commands
USER_COMMANDS:
LCALL READ_UART_WAIT_LONG
; cmd code in R3
MOV  A, R5
MOV  R3, A
CJNE A, #00, OP_NEXT0


;;  0 -- programming a data chuck
; get size, store in 0x17
LCALL READ_UART_WAIT_SHORT
MOV 0x1D, R5
; need to read  2(start_address) + size
; from 0x17 to 0x17  + 2 + size
MOV R0, 5
INC R0
INC R0
MOV R1, #0x1E

LOAD_DATA_ARRAY:
    LCALL READ_UART_WAIT_SHORT
    MOV @R1, 5
    INC R1
    DJNZ R0, LOAD_DATA_ARRAY
    JMP INVOKE_INTERNAL_EEPROM_MCRIO_PROGRAM


OP_NEXT0:
    CJNE    A, #01, OP_NEXT2
    
    
    ;; 1 -- programming byte-address pair
    LCALL READ_UART_WAIT_SHORT
    MOV A, R5
    MOV 0x1D, A
    JZ  INVOKE_INTERNAL_EEPROM_MCRIO_PROGRAM
    ; A *= 3
    RL  A
    ADD A, R5
    MOV R0, A
    MOV R1, #0x1E
    JMP LOAD_DATA_ARRAY


OP_NEXT2: 
    CJNE A, #03, OP_NEXT3
    ; 3 -- read block
    LCALL READ_UART_WAIT_SHORT
    MOV DPL,R5
    LCALL READ_UART_WAIT_SHORT
    MOV DPH,R5
    LCALL READ_UART_WAIT_SHORT
    MOV R4,5
    LCALL READ_UART_WAIT_SHORT
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
    CJNE A, #4, OP_NEXT4
    ;; 4 -- just echo
    ; load length
    LCALL READ_UART_WAIT_SHORT
    ECHO_NEXT_CHAR:
        MOV A, R3
        JZ  USER_COMMANDS
        LCALL READ_UART_WAIT_LONG ; wait longer
        JNB TI, $
        MOV SBUF, A
        DEC R5
        JMP ECHO_NEXT_CHAR

OP_NEXT4:
    JMP    EXIT_PROGRAM

INVOKE_INTERNAL_EEPROM_MCRIO_PROGRAM:
    ;; load delay of tWC 
    LCALL READ_UART_WAIT_SHORT
    MOV 0x1B, R5
    LCALL READ_UART_WAIT_SHORT
    MOV 0x1C, R5
    MOV  A, R3
    CPL  A
    MOV  B, A
    MOV  A, R3
    SETB PSW.1
    DB  0xA5
    CLR  PSW.1
    ;; give feedback to host
    JNB TI, $
    MOV A, R3
    CPL A
    MOV SBUF, A
    JMP    USER_COMMANDS 

READ_UART_WAIT_SHORT:
    LOAD_C16 R6,R7, WAIT_SHORT_MAX_COUNT
    JMP READ_UART

READ_UART_WAIT_LONG:
    LOAD_C16 R6,R7, WAIT_LONG_MAX_COUNT
    JMP  READ_UART

READ_UART:
    WAIT_UART_UNTIL_TIMEOUT:
        ; COUNTDOWN = WAIT_HANDSHAKE_MAX_COUNT;
        JNB   RI, READ_UART_COUNTDOWN
        MOV     R5, SBUF
        CLR     RI
        RET

    READ_UART_COUNTDOWN:
        ;; COUNT_DONW -= -1
        MOV     A, R6
        ORL     A, R7
        JZ      EXIT_PROGRAM


        MOV     A, R6
        DEC     R6
        JNZ     WAIT_UART_UNTIL_TIMEOUT

        DEC     R7
        JMP     WAIT_UART_UNTIL_TIMEOUT



EXIT_PROGRAM:
    CLR  REN
    EXIT_PROGRAMCLR_RI:
        CLR  RI
        JB   RI, EXIT_PROGRAMCLR_RI
    CLR A
    MOV B, A
    MOV DPL, A
    MOV DPL, A
    MOV PSW, A
    RET
END