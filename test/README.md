# Introduction
# Hardware and simulator support
I recommend that you implement these sfrs' function in your hardware design and simulator so that you can easily check that the test results are correct.

|address| register|function|
|:-: | :-:   |:-:|
|0xFC| EXR   |[Exit](##exit)|
|0xFD| PAR0  |[Assertion](##assertion)|
|0xFE| PAR1  |[Assertion](##assertion)|
|0xFF| AFUNC |[Assertion](##assertion)|


## Assertion
Assert function using 3 registers named `AFUNC`, `PAR1`, `PAR0`. `PAR0` and `PAR1` store the number you want to compare, AFUNC control comparison mode:

|value   | 0   | 1     |2       | 3     |
|:-:     |:-:  |:-:    |:-:     |:-:    |
|function| None|p0 > p1|p0 == p1|p0 < p1|

Assertions are the basic requirement for testing. It is used to check whether the results of certain instructions are correct. In the emulator, you can use assertions to verify that your .A51 is working as expected, making sure there are no human mistake in the .A51 file, so an assertion failure in the hardware design will tell you that there must be an error in hardware level.

## Exit
When you write a value greater than zero to `EXR`, it tells the simulator/hardware design tool that the program has exited.

Some simulators check if the program exits based on the length of data loaded in ROM. However, I still recommend that you implement this feature.
<!-- # Common testing process
1. write a 

When compare result not at expect, you'd better to check the soft
# Create new test -->















# manual test instructions
We first implement the following two instructions:
   - MOV direct, #immed
   - MOV direct, direct

 Why? using first instruction we can move any immediate number to any 
 address(include all SFR in RF). Using the second instruction, we can move
 any data from one memory cell/register to another memory cell/register.
 When we implement these two isntructions and make sure they work properly,
 then we can using  hardware assertion to check other instrcutions' result.
 (memory cell equal to immediate, ne register equal to another register etc).

# test table
|opcode|mnemonic|tested|
|:-|:-|:-|
|0x00|NOP     | |
|0x01| AJMP addr11  | |
|0x02| LJMP addr16  | |
|0x03| RR A   | |
|0x04| INC A   | |
|0x05| INC direct  | |
|0x06-0x07| INC @Ri | |
|0x08-0x0F| INC Rn  | |
|0x10| JBC bit, offset | |
|0x11| ACALL addr11  | |
|0x12| LCALL addr16  | |
|0x13| RRC A   | |
|0x14| DEC A   | |
|0x15| DEC direct  | |
|0x16-0x17| DEC @Ri | |
|0x18-0x1F| DEC Rn  | |
|0x20| JB bit, offset | |
|0x21| AJMP addr11  | |
|0x22| RET     | |
|0x23| RL A   | |
|0x24| ADD A, #immed   | |
|0x25| ADD A, direct   | |
|0x26-0x27| ADD A, @Ri  | |
|0x28-0x2F| ADD A, Rn   | |
|0x30| JNB bit, offset | |
|0x31| ACALL addr11  | |
|0x32| RETI     | |
|0x33| RLC A   | |
|0x34| ADDC A, #immed   | |
|0x35| ADDC A, direct   | |
|0x36-0x37| ADDC A, @Ri  | |
|0x38-0x3F| ADDC A, Rn   | |
|0x40| JC offset  | |
|0x41| AJMP addr11  | |
|0x42| ORL direct, A   | |
|0x43| ORL direct, #immed  | |
|0x44| ORL A, #immed   | |
|0x45| ORL A, direct   | |
|0x46-0x47| ORL A, @Ri  | |
|0x48-0x4F| ORL A, Rn   | |
|0x50| JNC offset  | |
|0x51| ACALL addr11  | |
|0x52| ANL direct, A   | |
|0x53| ANL direct, #immed  | |
|0x54| ANL A, #immed   | |
|0x55| ANL A, direct   | |
|0x56-0x57| ANL A, @Ri  | |
|0x58-0x5F| ANL A, Rn   | |
|0x60| JZ offset  | |
|0x61| AJMP addr11  | |
|0x62| XRL direct, A   | |
|0x63| XRL direct, #immed  | |
|0x64| XRL A, #immed   | |
|0x65| XRL A, direct   | |
|0x66-0x67| XRL A, @Ri  | |
|0x68-0x6F| XRL A, R0   | |
|0x70| JNZ offset  | |
|0x71| ACALL addr11  | |
|0x72| ORL C, bit  | |
|0x73| JMP @A+DPTR | |
|0x74| MOV A, #immed   | |
|0x75| MOV direct, #immed  |M|
|0x76-0x77| MOV @Ri, #immed | |
|0x78-0x7F| MOV Rn, #immed  | |
|0x80| SJMP offset  | |
|0x81| AJMP addr11  | |
|0x82| ANL C, bit  | |
|0x83| MOVC A, @A+PC    | |
|0x84| DIV AB  | |
|0x85| MOV direct, direct  | |
|0x86-0x87| MOV direct, @Ri | |
|0x88-0x8F| MOV direct, Rn  | |
|0x90| MOV DPTR, #immed    | |
|0x91| ACALL addr11  | |
|0x92| MOV bit, C  | |
|0x93| MOVC A, @A+DPTR  | |
|0x94| SUBB A, #immed   | |
|0x95| SUBB A, direct   | |
|0x96-0x97| SUBB A, @Ri  | |
|0x98-0x9F| SUBB A, Rn   | |
|0xA0| ORL C, /bit | |
|0xA1| AJMP addr11  | |
|0xA2| MOV C, bit  | |
|0xA3| INC DPTR    | |
|0xA4| MUL AB  | |
|0xA5|     | |
|0xA6-0xA7| MOV @Ri, direct | |
|0xA8-0xAF| MOV Rn, direct  | |
|0xB0| ANL C, /bit | |
|0xB1| ACALL addr11  | |
|0xB2| CPL bit | |
|0xB3| CPL C   | |
|0xB4| CJNE A, #immed, offset   | |
|0xB5| CJNE A, direct, offset   | |
|0xB6-0xB7| CJNE @Ri, #immed, offset | |
|0xB8-0xBF| CJNE Rn, #immed, offset  | |
|0xC0| PUSH direct  | |
|0xC1| AJMP addr11  | |
|0xC2| CLR bit | |
|0xC3| CLR C   | |
|0xC4| SWAP A   | |
|0xC5| XCH A, direct   | |
|0xC6-0xC7| XCH A, @Ri  | |
|0xC8-0xCF| XCH A, Rn   | |
|0xD0| POP direct  | |
|0xD1| ACALL addr11  | |
|0xD2| SETB bit | |
|0xD3| SETB C   | |
|0xD4| DA A   | |
|0xD5| DJNZ direct, offset  | |
|0xD6-0xD7| XCHD A, @Ri  | |
|0xD8-0xDF| DJNZ Rn, offset  | |
|0xE0| MOVX A, @DPTR    | |
|0xE1| AJMP addr11  | |
|0xE2| MOVX A, @R0  | |
|0xE3| MOVX A, @R1  | |
|0xE4| CLR A   | |
|0xE5| MOV A, direct   | |
|0xE6-0xE7| MOV A, @Ri  | |
|0xE8-0xEF| MOV A, Rn   | |
|0xF0| MOVX @DPTR, A    | |
|0xF1| ACALL addr11  | |
|0xF2-0xF3| MOVX @Ri, A  | |
|0xF4| CPL A   | |
|0xF5| MOV direct, A   | |
|0xF6-0xF7| MOV @Ri, A  | |
|0xF8-0xFF| MOV Rn, A   | |