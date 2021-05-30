# hm-51 Documention  <!-- omit in toc -->
---
## Table of Cotents  <!-- omit in toc -->
- [Introduction](#introduction)
- [Project Structure](#project-structure)
- [Check The Degin Before Anything](#check-the-degin-before-anything)
## Introduction
 hm-51 is a digital circuit project about 8051 CPU. The ultimate goal of hm-51 is to use common logic chip to build a CPU that supports MSC-51 ISA. I focus on two targets:

   - Support All MSC-51, which means we can write programs in C without worrying about which instructions we did not implement.
  
   - Keeping the hardware design on a smaller scale, which means that if we want to implement it using real commercially available DIP digital logic chips, we will not get a giant circuit.

In fact, we only care about the correct behavior of the instructions. I have never considered it to be consistent with the standard hardware behavior. I also discarded many non-essential SFRs to keep the circuit compact. Therefore, before starting any software work, you should read the summary [Don't assume what hardware doing] in [README-circ.md](README-circ.md).

The hardware design is hignly perosnalized, you can check the file [README-hd.md](README-hd.md) if you are interasted in my work. 

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
    - **testtools**
      - **compile.py** implementation of compile the .A51 file
      - **test_all.py** test all generate script in one folder
      - **test_process.py**
    - **51sim:** a 8051 insturction simulator.
    - **Digital:** a visual digital circuit desgin tool.
    - **alugen.bat** shortcut to generate ALUs' LUT file
    - **dscmp.bat** shortcut to compile decoder script

## Check The Degin Before Anything
 If the hardware design is not correct, it may cause inexplicable problems, so you should first check the design to ensure that the hardware is working correctly.

### Environment
  - python 3.8.0
  - A51.exe/BL51.exe/OH51.exe(keil C51 tools)
  - py51
 
  All other tools are provided in "tools" directory.

### Run test
 copy the following content to terminal:

 ```
 python3 tools/testtools/test_all.py test/generate/ temp/ 4
 ```


