# hm-51 Documention
---
## Introduction
 hm-51 is a digital circuit project about 8051 CPU. The ultimate goal of hm-51 is to use common logic chip to build a CPU that supports MSC-51 ISA. I focus on two targets:

   - Support All MSC-51, which means we can write programs in C without worrying about which instructions we did not implement.
  
   - Keeping the hardware design on a smaller scale, which means that if we want to implement it using real commercially available DIP digital logic chips, we will not get a giant circuit.

  In fact, we only care about the correct behavior of the instructions. I have never considered it to be consistent with the standard hardware behavior. I also discarded many non-essential SFRs to keep the circuit compact. Therefore, before starting any software work, you should read the summary [Hardware Behaviors and Resources](##hardware-behaviors-and-resources).

## Project Structure
  - **src**
    - **alu:** contain program to generate ALU LUT's binary file, see [README.md](src/alu/README.md).
    - **circuit:** contain all circuit design file
      - **CORE.dig:** main entry of circuit design.
    - **decoder:** contain all decoder script that describe deocder's LUT.
      - **decoder.ds:** main decoder script file.
    - **dscompiler:** It's an compiler of decoder script.
      - **compile.py:** main entry of compiler.
  - **test:** the tool and .A51 generate script used in test process.
    - **generate:** contain all *.A51 generate scripts.
    - **compile_verify.py:** used to compile-simulate-verify one .A51 file.
  - **tools**
    - **py51:** a 8051 insturction simulator.
    - **Digital:** a digital circuit desgin tool.
    - **alugen.bat**
    - **dscmp.bat**
    - **test_all.bat**
    - **test_one.bat**

## Check The Degin Before Anything
 If the hardware design is not correct, it may cause inexplicable problems, so you should first check the design to ensure that the hardware is working correctly.

### Environment
  - python 3.8.0
  - A51.exe/BL51.exe/OH51.exe(keil C51 tools)
 
  All other tools are provided in "tools" directory.

### Run test
 copy the following content to terminal:

 ```
 python3 tools/test_all.py test/generate/ temp/
 ```

## Hardware Behaviors and Resources 


### don't assume what hardware doing
In standard 8051 cpu, you might using some trick based on hardware behavior.

For example, assume lower byte of 16-bit XRAM's address are connected to `P0`, higher byte is connected to `P2`, `R0 = 1`,`DPTR = 0xFF01`,`XRAM[1] = 3`,`XRAM[0xFF01] = 4`  what the result of `A` after the following code are executed?

```
MOVX A, @DPTR
MOVX A, @R0
```
You might say: Obviously, `MOV A, @DPTR` will make `A = 4` , but it's will also make `P0 = 0x01`,`P2 = 0xFF`. When we use `MOVX A, @R0`, it's only make `P0 = R0`,that is, `P0 = 1`, so the 16-bit address is also 0xFF01, which means `A = 4` too.

 But, in my design, `MOVX A, @DPTR` is just move data from external address according to DPTR's value,`P0` and `P1` are not exist in CPU core.

 In theory, `MOVX A, @R0` just provide a 8-bit address of extrnal RAM, You should not assume the higher 8-bit address value.

What you should do is read this chapter to understand how to connect peripheral devices(XRAM, SFR, etc), the behavior of external components is up to you.