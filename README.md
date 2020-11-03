# hm-51 Documention
---
## Table of Cotents 
  - [Introduction](#introduction)
  - [Project Structure](#project-structure)
  - [Check The Degin Before Anything](#check-the-degin-before-anything)
    - [Environment](#environment)
    - [Run test](#run-test)
  - [Don't Assume What Will Hardware Doing](#dont-assume-what-will-hardware-doing)
  - [Logical Design And Resources Of The Circuit](#logical-design-and-resources-of-the-circuit)
    - [Interface](#interface)
    - [Core resource](#core-resource)
    - [Add SFR](#add-sfr)
    - [Interrupt](#interrupt)
    
## Introduction
 hm-51 is a digital circuit project about 8051 CPU. The ultimate goal of hm-51 is to use common logic chip to build a CPU that supports MSC-51 ISA. I focus on two targets:

   - Support All MSC-51, which means we can write programs in C without worrying about which instructions we did not implement.
  
   - Keeping the hardware design on a smaller scale, which means that if we want to implement it using real commercially available DIP digital logic chips, we will not get a giant circuit.

In fact, we only care about the correct behavior of the instructions. I have never considered it to be consistent with the standard hardware behavior. I also discarded many non-essential SFRs to keep the circuit compact. Therefore, before starting any software work, you should read the summary [Don't assume what hardware doing](#dont-assume-what-hardware-doing).

The majority of this document is introduction of resources which in circuit simulation file. although the practical hardware is slightly differ to software simulation, I always put the hardware introduction into a separate file due to timing constraints and drive capabilities.

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
 python3 tools/test_all.py test/generate/ temp/
 ```


## Don't Assume What Will Hardware Doing
In standard 8051 cpu, you might using some trick based on hardware behavior.

For example, assume lower byte of 16-bit XRAM's address are connected to `P0`, higher byte is connected to `P2`, `R0 = 1`,`DPTR = 0xFF01`,`XRAM[1] = 3`,`XRAM[0xFF01] = 4`  what the result of `A` after the following code are executed?

```
MOVX A, @DPTR
MOVX A, @R0
```
You might say: it's Obvious, `MOV A, @DPTR` will make `A = 4` , but it's will also make `P0 = 0x01`,`P2 = 0xFF`. When we use `MOVX A, @R0`, it's only make `P0 = R0`,that is, `P0 = 1`, so the 16-bit address is also 0xFF01, which means `A = 4` too.

 But, in my design, `MOVX A, @DPTR` is just move data from external address according to DPTR's value,`P0` and `P1` are not exist in CPU core.

 In theory, `MOVX A, @R0` just provide a 8-bit address of extrnal RAM, You should not assume the higher 8-bit address value.

What you should do is read this chapter to understand how to connect peripheral devices(XRAM, SFR, etc), the behavior of external components is up to you.

## Logical Design And Resources Of The Circuit
I will intruduce the logic design and resources in the circuit simulation file, the hardware design's should see in another README.md file.

### Interface
Although there are some default peripherals in the design, but they are only for testing and may behave differently compared to other CPUs. So, there will introduce the interface of CORE.dig so that you can attach your components to it.

However, if you are lazy or intreasted in peripherals, don't worry, It's not powerful but easy to use, you can see the details in there.

``` python
      ╔════════════════╗
──/1──╢>CLKI       CLKO╟───/1───
──/1──╢/CLR          IO╟───/8───
──/1──╢MC       /SFR_WE╟───/1───
──/1──╢SW       /SFR_OE╟───/1───
──/1──╢Go       IRR_CLR╟───/8───
──/1──╢Stall    Address╟──/8───
──/8──╢IRR_IN          ║
      ║                ║
      ╚════════════════╝     

```
  - CLKI
    - the clock input, used to generate the main clock of the CPU and the WE pulse of the asynchronous RAM chip. In the current design, 12MHz is preferred.
  
  - CLKO
    - CPU's main clock, provide clock to peripherals(SFR).
  - Run Control
    - MC, manual clock, using this to step each microinstruction when SW is high. It's contain synchronization circuit, so it's suitable for manual operatation.
    - SW, switch between manual clock or free run. It's contain synchronization circuit, so it's suitable for manual operatation.
    - Go, let CORE leave stall state. It's contain synchronization circuit, so it's suitable for manual operatation.
    - Stall, let CORE enter stall state immediately.
  
 - IO Pin
   -  output data when writing SFR.
   -  receive data when reading SRF.
  
-  Control Pin
   - IRR_IN, connect IRR to this so that CPU can check if there are interrupt happend.
   -  IRR_CLRB, clear IRR bit according to this control.
   -  /SFR_WE, SFR write enable,active low, prepared for clocked chip.
   -  /SFR_OE, SFR output enable, active low.
   
 - Address Pin
   - using to select SFR by RAM address.

### Core resource
 - RAM, 0x100 byte
 - XRAM 0x10000 bytes
 - ROM  0x10000 bytes
 - SFR  A,B,SP,PSW,DPL,DPH,IE,IP 

### Add SFR
 When adding SFR, the input/ouput pin of the device should be connected to the IO pin of CPU, the higher 8-bit of the address pin of the CPU will ouput the SFR address, and your device should check the address to ensure that the CPU is trying to operate it. 

  In the case of CPU operating you deivce, when `SFR_OE` is hight, your device must ouput the desired content to the IO pin, and when `SFR_WE` is high, your device should accept then value of the IO Pin.

  Howerver, no matter what, the device's read/write behavior is designed by you.

 This is an example, an simple register are mapped in address 0xE2.
  ```
    ╔══════════╗
    ║          ║        ┌──────────────────────────────────────────┐
    ║        IO╟───/8───┥         ╔═════════╗     ┌────────────┐   |
    ║          ║        └─────────╢D  REG  Q╟─/8──|trisatebuffer>──┘ 
    ║      CLKO╟──────────────────╢>CLK     ║     └───────┯────┘ 
    ║          ║              ┌───╢WE       ║             |OE
    ║          ║           ╔═╗|   ╚═════════╝             |
    ║   /SFR_WE╟───/1─╢~╟──╢&╟┘                           |
    ║          ║       MD ─╢ ║     ╔═╗                    |
    ║          ║           ╚═╝ MD ─╢&╟────────────────────┘
    ║   /SFR_OE╟───/1────╢~╟───────╢ ║               
    ║          ║        0-7        ╚═╝               
    ║          ║              ╔══════════╗                                        
    ║          ║              ║Comparator║                                            
    ║   Address╟───/8─────────╢ A       Q╟─ MD                                          
    ╚══════════╝        0xE2──╢ B        ║                                          
                              ╚══════════╝      
  ```





### Interrupt
  When `IRR_IN` should connect to IRR output, `IRR_IN[0]` should be the highest priority interrupt request, and `IRR_IN[7]` should be the lowest priority interrupt request.

  At some point after the CPU accepts the interrupt, the CPU will set `IRR_CLR[N]` to 1. If there are any interrupt bits to be cleared by the CPU (such as IT0, IT1) instead of clearing the interrupt register bits (such as TI, RI) by software, you should clear the corresponding interrupt request bits `IRR[N]` in the register at this time.


  ```
    ╔═════════════╗        ╔═════════╗
    ║          CLK╟───/8───╢>        ║
   ┌╢IRR_IN     IO╟───/8───╢   IRR  Q╟─┐
   |║      IRR_CLR╟───/8───╢         ║ |                    
   |╚═════════════╝        ╚═════════╝ |                      
   └───────────────────────────────────┘                                   
  ```
  Here is an example of IRR logic.

  ``` 
                                ╔════════╗
    CLK ────────────────────────╢>CLK   Q╟─┐
    IRQ ───────────────┐  ╔═╗   ║ IRR[0] ║ |     
                   ╔═╗ └──╢|╟───╢ D      ║ |     
  /IRR_CLR[N]──────╢&╟────╢ ║   ╚════════╝ |                  
                 ┌─╢ ║    ╚═╝              | 
                 | ╚═╝                     |            
                 └─────────────────────────┘        
  ```

