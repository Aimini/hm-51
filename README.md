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

### interface

``` python
      ╔════════════╗
──/1──╢>CLKI   CLKO╟───/1───
      ║            ║
      ║          IO╟───/8───
      ║            ║
      ║     IRQ_CLR╟───/1───
      ║     /IRQ_OE╟───/1───
      ║     /SFR_WE╟───/1───
      ║     /SFR_OE╟───/1───
      ║   /XRAM_AWE╟───/1───
      ║    /XRAM_OE╟───/1───
      ║            ║
      ║     Address╟──/16───
      ║            ║
      ╚════════════╝     

```
  - CLKI
    - the clock input, used to generate the main clock of the CPU and the WE pulse of the asynchronous RAM chip. In the current design, 12MHz is preferred.
  
  - CLKO
    - CPU's main clock, provide clock to peripherals(SFR).

 - IO Pin
   -  output data when writing SFR/XRAM.
   -  receive data when reading SRF/XRAM.
   -  receive IRQs when checking interrupt.
   -  output IRQ to when CPU wants you to clear this IRQ.
  
-  Control Pin
   -  IRQ_CLR, clear IRQ according IO pin value.
   -  IRQ_OE, IRQs output enable.
   -  /SFR_WE, SFR write enable,active low, prepared for clocked chip.
   -  /SFR_OE, SFR output enable, active low.
   -  /XRAM_AWE, RAM write enable, active low, prepared for async chip.
   -  /XRAM_OE, RAM output enable, active low.
   
 - Address Pin
   - using all 16 bits when operating XRAM
   - using higher 8 bits when operating SFR by RAM address.

### add SFR
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
    ║          ║      ┌─────     ╔══════════╗                                        
    ║   Address╟──/16─┥ 8-15     ║Comparator║                                            
    ║          ║      └──────────╢ A       Q╟─ MD                                          
    ╚══════════╝           0xE2──╢ B        ║                                          
                                 ╚══════════╝      
  ```




### add XRAM
 XRAM is controlled by `Address`, `/XRAM_AWE` and `/XRAM_OE`. Remember, `/XRAM_AWE` is a short low pulse before rasing edge of `CLKO`, so an asynchronous SRAM chip is required.

  ```
    ╔══════════╗               ╔═════════╗
    ║        IO╟─────/8────────╢IO       ║
    ║   Address╟─────/16───────╢ADDR     ║ 
    ║ /XRAM_AWE╟─────/1────────╢/WE      ║                   
    ║  /XRAM_OE╟─────/1────────╢/OE      ║                                           
    ╚══════════╝               ╚═════════╝                                          
                                   
  ```

### Interrupt
  When `/IRQ_OE` is 0, you should output IRQ to IO BUS, `BUS[0]` should be the highest priority interrupt request, and `BUS[7]` should be the lowest priority interrupt request.

  At some point after the CPU accepts the interrupt, the CPU will set `IRQ_CLR` to 1. If there are any interrupt bits to be cleared by the CPU (such as IT0, IT1) instead of clearing the interrupt register bits (such as TI, RI) by software, you should clear the corresponding interrupt request bits in the register at this time.

  If the CPU finds that the IRQ in `BUS[0]` is the highest priority interrupt request, then `BUS[0]` will output `0b00000001` when `IRQ_CLR` is 1. And, if the `BUS[1]` is the highest priority interrupt request, then `BUS[0]` will output `0b00000010`.

  ```
    ╔═════════════╗        ╔═════════╗
    ║          CLK╟───/8───╢>        ║
    ║           IO╟───/8───╢   IRR   ║
    ║      IRQ_CLR╟───/1───╢         ║
    ║      /IRQ_OE╟───/1───╢         ║                           
    ╚═════════════╝        ╚═════════╝                         
                                   
  ```
  Here is an example of IRR logic.

  ``` 
                                ╔════════╗
    CLK ────────────────────────╢>CLK   Q╟─┐
    IRQ ───────────────┐  ╔═╗   ║ IRR[0] ║ |     
            ╔═╗    ╔═╗ └──╢|╟───╢ D      ║ |     
   IRQ_CLR ─╢&╟o───╢&╟────╢ ║   ╚════════╝ |                  
    BUS[0] ─╢ ║  ┌─╢ ║    ╚═╝              | 
            ╚═╝  | ╚═╝                     |                                       
                 └─────────────────────────┘        
  ```