# Test Case Document  <!-- omit in toc -->
---
# Table of Content  <!-- omit in toc -->
- [Hardware and simulator requirment](#hardware-and-simulator-requirment)
- [Manual test instructions](#manual-test-instructions)
- [Test table](#test-table)
- [The test case](#the-test-case)



## Hardware and simulator requirment

I recommend that you implement these SFRs' function in your hardware design and instruction simulator so that you can easily check that the test results are correct.

| address | register |         function         |
|:--------|----------|:------------------------:|
| 0xFB    | DUMP     |      [dump](#dump)      |
| 0xFC    | EXR      |      [exit](#exit)      |
| 0xFD    | PAR0     | [assertion](#assertion) |
| 0xFE    | PAR1     | [assertion](#assertion) |
| 0xFF    | AFUNC    | [assertion](#assertion) |


### assertion

Assert function using 3 registers named `AFUNC` , `PAR1` , `PAR0` . `PAR0` and `PAR1` store the number you want to compare, AFUNC control comparison mode:

| value    | 0    | 1       | 2        | 3       | 4       |
|:---------|:-----|:--------|:---------|:--------|:--------|
| function | None | p0 > p1 | p0 == p1 | p0 < p1 | STOP    |

Assertions are the basic requirement for testing. It is used to check whether the results of certain instructions are correct. In the emulator, you can use assertions to verify that your . A51 is working as expected, making sure there are no human mistake in the . A51 file, so an assertion failure in the hardware design will tell you that there must be an error in hardware level.

### exit

When you write a value greater than zero to `EXR` , it tells the simulator/hardware design tool that the program has exited.

Some simulators check if the program exits based on the length of data loaded in ROM. However, I still recommend that you implement this feature.

### dump

When you write an `DUMP` value greater than zero, it tells the simulator / hardware design tool to dump the value of IRAM and the value of the register to a file.

The registers you want to dump, the IRAM range you want to dump, and the file format are determined by your design. 

The ultimate goal is that you can determine whether the hardware design is correct by comparing the contents of the simulator dump results and the hardware design tool dump results.


## Manual test instructions

We first implement the following four instructions:
   - 0x75: MOV direct, #immed
   - 0x85: MOV direct, direct
   - 0x76-0x77: MOV @Ri, #immed
   - 0x86-0x87: MOV direct, @Ri
  
 *why `MOV direct, #immed` and `MOV direct,direct`?*

 In our verification process, it's simply executes instructions and checks whether the results meet our expectations. Therefore,loaing immediate values to registers/memory is the basis of all test cases.
 
 For example, you want to check the instruction `ADD A, R0`, you must write an assertion:

   - load 3 to `A`
   - load 4 to `R0`
   - check if `A == 7` after `ADD A, R0` executed.

 As you can see, we need to use #immed in many scenarios. Register A,register B, R0-R7 and direct address, most of these registers/memory can accessed by direct address(SFR). Therefore, you should first implement `MOV direct, #immed`.

But, in more detail, how do we use assertions? Using the previous `ADD A, R0` example, we should do that:

 - load 7 to `ARG0`
 - load `A` to `ARG1`
 - load 2 to `AFUNC`

What we need to pay attention to is how to load `A` into `ARG1`. Obviously,`MOV direct, direct` are the most common instructions, because for most instructions, their destination can be accessed by direct address.

 *why `MOV @Ri, #immed` and `MOV direct,@Ri`?*

 There are some instructions using indirect address. The reason is the same as direct address.

 *that's all*

 Of course, there are a few instructions (MOVX, MOVC) that involve other types of addresses, but they only move data between XRAM / ROM and RAM, and the generation script will test move to and move back in pairs.

 When we implement these four isntructions and make sure they work properly, then we can using hardware assertion to check other instrcutions' result. (memory cell equal to immediate, ne register equal to another register etc).

## Test table

| opcode    | mnemonic                 | tested |
|:----------|:-------------------------|:------:|
| 0x00      | NOP                      |   Y    |
| 0x01      | AJMP addr11              |   Y    |
| 0x02      | LJMP addr16              |   Y    |
| 0x03      | RR A                     |   Y    |
| 0x04      | INC A                    |   Y    |
| 0x05      | INC direct               |   Y    |
| 0x06-0x07 | INC @Ri                  |   Y    |
| 0x08-0x0F | INC Rn                   |   Y    |
| 0x10      | JBC bit, offset          |   Y    |
| 0x11      | ACALL addr11             |   Y    |
| 0x12      | LCALL addr16             |   Y    |
| 0x13      | RRC A                    |   Y    |
| 0x14      | DEC A                    |   Y    |
| 0x15      | DEC direct               |   Y    |
| 0x16-0x17 | DEC @Ri                  |   Y    |
| 0x18-0x1F | DEC Rn                   |   Y    |
| 0x20      | JB bit, offset           |   Y    |
| 0x21      | AJMP addr11              |   Y    |
| 0x22      | RET                      |   Y    |
| 0x23      | RL A                     |   Y    |
| 0x24      | ADD A, #immed            |   Y    |
| 0x25      | ADD A, direct            |   Y    |
| 0x26-0x27 | ADD A, @Ri               |   Y    |
| 0x28-0x2F | ADD A, Rn                |   Y    |
| 0x30      | JNB bit, offset          |   Y    |
| 0x31      | ACALL addr11             |   Y    |
| 0x32      | RETI                     |   Y    |
| 0x33      | RLC A                    |   Y    |
| 0x34      | ADDC A, #immed           |   Y    |
| 0x35      | ADDC A, direct           |   Y    |
| 0x36-0x37 | ADDC A, @Ri              |   Y    |
| 0x38-0x3F | ADDC A, Rn               |   Y    |
| 0x40      | JC offset                |   Y    |
| 0x41      | AJMP addr11              |   Y    |
| 0x42      | ORL direct, A            |   Y    |
| 0x43      | ORL direct, #immed       |   Y    |
| 0x44      | ORL A, #immed            |   Y    |
| 0x45      | ORL A, direct            |   Y    |
| 0x46-0x47 | ORL A, @Ri               |   Y    |
| 0x48-0x4F | ORL A, Rn                |   Y    |
| 0x50      | JNC offset               |   Y    |
| 0x51      | ACALL addr11             |   Y    |
| 0x52      | ANL direct, A            |   Y    |
| 0x53      | ANL direct, #immed       |   Y    |
| 0x54      | ANL A, #immed            |   Y    |
| 0x55      | ANL A, direct            |   Y    |
| 0x56-0x57 | ANL A, @Ri               |   Y    |
| 0x58-0x5F | ANL A, Rn                |   Y    |
| 0x60      | JZ offset                |   Y    |
| 0x61      | AJMP addr11              |   Y    |
| 0x62      | XRL direct, A            |   Y    |
| 0x63      | XRL direct, #immed       |   Y    |
| 0x64      | XRL A, #immed            |   Y    |
| 0x65      | XRL A, direct            |   Y    |
| 0x66-0x67 | XRL A, @Ri               |   Y    |
| 0x68-0x6F | XRL A, R0                |   Y    |
| 0x70      | JNZ offset               |   Y    |
| 0x71      | ACALL addr11             |   Y    |
| 0x72      | ORL C, bit               |   Y    |
| 0x73      | JMP @A+DPTR              |   Y    |
| 0x74      | MOV A, #immed            |   Y    |
| 0x75      | MOV direct, #immed       |   M    |
| 0x76-0x77 | MOV @Ri, #immed          |   M    |
| 0x78-0x7F | MOV Rn, #immed           |   Y    |
| 0x80      | SJMP offset              |   Y    |
| 0x81      | AJMP addr11              |   Y    |
| 0x82      | ANL C, bit               |   Y    |
| 0x83      | MOVC A, @A+PC            |   Y    |
| 0x84      | DIV AB                   |   Y    |
| 0x85      | MOV direct, direct       |   M    |
| 0x86-0x87 | MOV direct, @Ri          |   M    |
| 0x88-0x8F | MOV direct, Rn           |   Y    |
| 0x90      | MOV DPTR, #immed         |   Y    |
| 0x91      | ACALL addr11             |   Y    |
| 0x92      | MOV bit, C               |   Y    |
| 0x93      | MOVC A, @A+DPTR          |   Y    |
| 0x94      | SUBB A, #immed           |   Y    |
| 0x95      | SUBB A, direct           |   Y    |
| 0x96-0x97 | SUBB A, @Ri              |   Y    |
| 0x98-0x9F | SUBB A, Rn               |   Y    |
| 0xA0      | ORL C, /bit              |   Y    |
| 0xA1      | AJMP addr11              |   Y    |
| 0xA2      | MOV C, bit               |   Y    |
| 0xA3      | INC DPTR                 |   Y    |
| 0xA4      | MUL AB                   |   Y    |
| 0xA5      |                          |   Y    |
| 0xA6-0xA7 | MOV @Ri, direct          |   Y    |
| 0xA8-0xAF | MOV Rn, direct           |   Y    |
| 0xB0      | ANL C, /bit              |   Y    |
| 0xB1      | ACALL addr11             |   Y    |
| 0xB2      | CPL bit                  |   Y    |
| 0xB3      | CPL C                    |   Y    |
| 0xB4      | CJNE A, #immed, offset   |   Y    |
| 0xB5      | CJNE A, direct, offset   |   Y    |
| 0xB6-0xB7 | CJNE @Ri, #immed, offset |   Y    |
| 0xB8-0xBF | CJNE Rn, #immed, offset  |   Y    |
| 0xC0      | PUSH direct              |   Y    |
| 0xC1      | AJMP addr11              |   Y    |
| 0xC2      | CLR bit                  |   Y    |
| 0xC3      | CLR C                    |   Y    |
| 0xC4      | SWAP A                   |   Y    |
| 0xC5      | XCH A, direct            |   Y    |
| 0xC6-0xC7 | XCH A, @Ri               |   Y    |
| 0xC8-0xCF | XCH A, Rn                |   Y    |
| 0xD0      | POP direct               |   Y    |
| 0xD1      | ACALL addr11             |   Y    |
| 0xD2      | SETB bit                 |   Y    |
| 0xD3      | SETB C                   |   Y    |
| 0xD4      | DA A                     |   Y    |
| 0xD5      | DJNZ direct, offset      |   Y    |
| 0xD6-0xD7 | XCHD A, @Ri              |   Y    |
| 0xD8-0xDF | DJNZ Rn, offset          |   Y    |
| 0xE0      | MOVX A, @DPTR            |   Y    |
| 0xE1      | AJMP addr11              |   Y    |
| 0xE2      | MOVX A, @R0              |   Y    |
| 0xE3      | MOVX A, @R1              |   Y    |
| 0xE4      | CLR A                    |   Y    |
| 0xE5      | MOV A, direct            |   Y    |
| 0xE6-0xE7 | MOV A, @Ri               |   Y    |
| 0xE8-0xEF | MOV A, Rn                |   Y    |
| 0xF0      | MOVX @DPTR, A            |   Y    |
| 0xF1      | ACALL addr11             |   Y    |
| 0xF2-0xF3 | MOVX @Ri, A              |   Y    |
| 0xF4      | CPL A                    |   Y    |
| 0xF5      | MOV direct, A            |   Y    |
| 0xF6-0xF7 | MOV @Ri, A               |   Y    |
| 0xF8-0xFF | MOV Rn, A                |   Y    |

## The test case

 In fact, it is tedious to manually write a bunch of code to test edge conditions or normal conditions, So we will use the script to generate assembly code.

 You should follow the following rules so that the test case runner(TCR) can invoke the generate script and correctly execute the compilation and run verification process.

### create new test case


 Enter into ``/test/generate`` directory, then you should create a sub-package(namely, a folder) to contain your script. 
 
 For example then sub-package's name is ``mytest``, then you should create a ".py" file in it, for example ``testbalabala.py``. finally, you get a structure like ``test/generate/mytest/testbalabala.py``.

 In ``testbalabala.py``, you should create a variable ``p`` and it must be the instance of the ``asm_test``(see ``test/generate/testutil.py``)

 Now you can try to add some string of A51 code to ``p``.
### run it
 Assume that you already written the test code on ``test/generate/mytest/testbalabala.py``, and you want all temporary output be in the ``./temp``, you cnas use this:

 ``` bash
  python ./test/test_process.py -A -H -A -C -m generate.mytest -f testbalabala.py -o ./temp
 ```
