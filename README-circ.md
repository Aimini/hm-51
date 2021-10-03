# hm-51 Logic Circuit Design Documention  <!-- omit in toc -->

---
## Table of Cotents  <!-- omit in toc -->
- [Introductions](#introductions)
- [Don't Assume What Will Hardware Doing](#dont-assume-what-will-hardware-doing)
- [Logical Design And Resources Of The Circuit](#logical-design-and-resources-of-the-circuit)

## Introductions
The majority of this document is the introduction of resources which in circuit simulation file. although the practical hardware is slightly differ to software simulation, I always put the hardware introduction into a [README-hd.md](README-hd.md) due to timing constraints and drive capabilities.

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

``` 
      ╔════════════════╗
──/1──╢>CLK_in       PC╟───/16───
──/1──╢/CLR        MIPC╟───/12───
──/8──╢IRQ_IN       CLK╟───/1───
──/1──╢MC         BUS_D╟───/8───
──/1──╢SW       Address╟───/8───    
──/1──╢Go       ~SFR_WE╟───/1───
──/1──╢Stall    ~SFR_OE╟───/1───
      ║       ~IRR_CLRB╟───/8─── 
      ╚════════════════╝     

```
  - CLK_in
    - the clock input, used to generate the main clock of the CPU and the WE pulse of the asynchronous RAM chip. In the current design, 12MHz is preferred.
  
  - CLK
    - CPU's main clock, provide clock to peripherals(SFR).
  
  - Run Control
    - MC, manual clock, using this to step each micro-instruction when SW is high. It's contain synchronization circuit, so it's suitable for manual operatation.
    - SW, switch between manual clock or free run.
    - Go, let CORE leave stall state.
    - Stall, let CORE enter stall state immediately.
  
 - Data bus
   -  BUS_D, output data when writing SFR, receive data when reading SFR.
  
-  Control Pin
   -  IRQ_IN, connect this to interrupt requests so that CPU can check if there are any interrupt happend.
   -  ~IRR_CLRB, clear IRR bit according to this control.
   -  /SFR_WE, SFR write enable,active low, prepared for clocked chip.
   -  /SFR_OE, SFR output enable, active low.
   
 - Address Pin
   - Address， using to select SFR by RAM address.

### Core resource
 - RAM, 0x100 byte
 - XRAM 0x10000 bytes
 - ROM  0x10000 bytes
 - SFR  A,B,SP,PSW,DPL,DPH,IE,IP 

### Add SFR
 When adding SFR, the input/output pin of the device should be connected to the IO pin of CPU, the higher 8-bit of the address pin of the CPU will output the SFR address, and your device should check the address to ensure that the CPU is trying to operate it. 

  In the case of CPU operating you deivce, when `SFR_OE` is hight, your device must output the desired content to the IO pin, and when `SFR_WE` is high, your device should accept then value of the IO Pin.

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
    ║   ~SFR_WE╟───/1─╢~╟──╢&╟┘                           |
    ║          ║       MD ─╢ ║     ╔═╗                    |
    ║          ║           ╚═╝ MD ─╢&╟────────────────────┘
    ║   ~SFR_OE╟───/1────╢~╟───────╢ ║               
    ║          ║        0-7        ╚═╝               
    ║          ║              ╔══════════╗                                        
    ║          ║              ║Comparator║                                            
    ║   Address╟───/8─────────╢ A       Q╟─ MD                                          
    ╚══════════╝        0xE2──╢ B        ║                                          
                              ╚══════════╝      
  ```





### Interrupt
  In the current design, the IRRs ordered by priority are IT0, TF0, IT1, TF1 and (RI | TI).

  In principle, the `IRR_IN` should connect to IRR output, `IRR_IN[0]` should be the highest priority interrupt request, and `IRR_IN[7]` should be the lowest priority interrupt request.

  At some point after the CPU accepts the interrupt, the CPU will set `~IRR_CLR[N]` to 1. If there are any interrupt bits to be cleared by the CPU (such as IT0, IT1) instead of clearing the interrupt register bits (such as TI, RI) by software, you should clear the corresponding interrupt request bits `IRR[N]` in the register at this time.


  Here is an example of IRR logic.

  ``` 
                                ╔════════╗
    CLK ────────────────────────╢>CLK   Q╟─┐
    IRQ ───────────────┐  ╔═╗   ║ IRR[0] ║ |     
                   ╔═╗ └──╢|╟───╢ D      ║ |     
  ~IRR_CLR[0]──────╢&╟────╢ ║   ╚════════╝ |                  
                 ┌─╢ ║    ╚═╝              | 
                 | ╚═╝                     |            
                 └─────────────────────────┘        
  ```


### SFR and Peripherals
 All available SFRs are listed in the following table, The internal SFR are marked in bold
 and the SFRs that only implement part of standard function will included in parentheses.
| Address |    0    |   1    |    2    |    3    |   4   | 5     | 6 | 7 |
|:-------:|:-------:|:------:|:-------:|:-------:|:-----:|:------|:-:|:-:|
|   F8    |         |        |         |         |       |       |   |   |
|   F0    |  **B**  |        |         |         |       |       |   |   |
|   E8    |         |        |         |         |       |       |   |   |
|   E0    | **ACC** |        |         |         |       |       |   |   |
|   D8    |         |        |         |         |       |       |   |   |
|   D0    | **PSW** |        |         |         |       |       |   |   |
|   C8    |         |        |         |         |       |       |   |   |
|   C0    |         |        |         |         |       |       |   |   |
|   B8    | **IP**  |        |         |         |       |       |   |   |
|   B0    |         |        |         |         |       |       |   |   |
|   A8    | **IE**  |        |         |         |       |       |   |   |
|   A0    |         |        |         |         |       |       |   |   |
|   98    | (SCON)  |  SBUF  |         |         |       |       |   |   |
|   90    |  (P1)   |        |         |         |       |       |   |   |
|   88    |  TCON   | (TMOD) |  (TL0)  |  (TL1)  | (TH0) | (TH1) |   |   |
|   80    |  (P0)   | **SP** | **DPL** | **DPH** |       |       |   |   |


#### P0(0x80), P1(0x90)
|      Bit      |  7  |  6  |  5  |  4  |  3  | 2   |  1  |  0  |
|:-------------:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Accessibility | R/W | R/W | R/W | R/W | R/W | R/W | R/W | R/W |

`P0` `P1` are connect to 8 digit 7-segment display.
`P0`'s each bit was used to select the digit,
 `P0[0]` coressponds to digtal 0(far right) and `P0[7]` is used to select digit 7 (far left).


 P1 is used to light the segments in one digit, `P1[0]` to `P1[7]` are corresponding to `a~g, dp`.


#### TCON(0x88)
|      Bit      |  7  |  6  |  5  |  4  |  3  |  2  |  1  |  0  |
|:-------------:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
|     Name      | TF1 | TR1 | TF0 | TR0 | IE1 | IT1 | IE0 | IT0 |
| Accessibility | R/W | R/W | R/W | R/W | R/W | R/W | R/W | R/W |

All bits in this TCON are readable and writable and it's function is consistent with the standand. 
  - IT0 : The interrupt type of external interrupt 0. When it is 0, the type is level trigger, otherwise, it is falling edge trigger.
  - IE0 : Interrupt 0 flag, set to 1 when  external interrupt 0 occurred, automatically cleared when returning from the corresponding interrupt routine(return by RETI).
  - IT1, IE1 : Same function as interrupt 0, just relevant to interrupt 1.

  - TR0: Timmer0 enable bit, timmer0 only start to count when it is 1.
  - TF0: Timmer1 overflow bit, set when Timmer0 is overflows(set).
  - TR1, TF1: Same function as Timmer0, just relevant to timmer1.
#### TMOD(0x89)
|      Bit      |  7  |  6   | 5 | 4 |  3  |  2  | 1 | 0 |
|:-------------:|:---:|:----:|:-:|:-:|:---:|:---:|:-:|:-:|
|     Name      |GATE1| C/~T1| X | X |GATE0|C/~T0| X | X |
| Accessibility | R/W | R/W  | X | X | R/W | R/W | X | X |

  The function of timmer is different from standard.

  - GATE_n : When TR_n is 1, The timmer_n will only start to count when ~XINT_n is 1.
  - C/~T_n : When TR_n is 1, regarding the GATE_n, the timmer_n will count 1 when there is falling edge at ~XINT_n.

  
#### TL0(0x8A), TL1(0x8B), TH0(0x8C), TH1(0x8D)
|      Bit      | 7 - 0 |
|:-------------:|:-----:|
| Accessibility |   W   |

TLn and THn will form a 16-bit timmer named 'timmern', when you write value to TLn and THn, you are actully writing the reaload value for this timmern,
and the timmern will automatically load the value when overflow or timmer is disabled.

``` MIPS
MOV TL0, 0x00
MOV TH0, 0xFF  ; count from 0xFF00  to 0xFFFF, 0x100 cycle total.
MOV TCON, 0x20 ; eable timmer 0

INT_TIMMER0:
  #do something
  reti
```

#### SCON(0x98)
|      Bit      | 7 | 6 | 5 | 4 | 3 | 2 |  1  |  0  |
|:-------------:|:-:|:-:|:-:|:-:|:-:|:--|:---:|:---:|
|     Name      | X | X | X | X | X | X | TI  | RI  |
| Accessibility | X | X | X | X | X | X | R/W | R/W |

This register is used to indicate SBUF's state. 
  - RI: set when SBUF received a byte.
  - TI: set when byte in SBUF was sent. actually the simulator will can send the data immediately, but we have this bit just for letting the same code be suitable to hardware.

 notice: you should set TI at first place before sending any data. RI and TI won't be cleared by hardware.


``` MIPS
; interrupt routine example
INT_SERIAL:
  JB  RI, SERIAL_REC:
  JB  TI, SERIAL_SENT:
  ;opss! what's wrong here?
SERIAL_REC:
  ;do something relate to recived byte
  CLR RI 
  reti

SERIAL_SENT:
  ;do something relate to byte sent
  CLR TI
  reti
```

#### SBUF(0x99)
|      Bit      | 7 - 0 |
|:-------------:|:-----:|
| Accessibility |  R/W  |

Writing a byte to SBUF will start the process of sending bytes via UART,
 while reading SBUF will read the most recently received byte.
 There is a buffer in serial receive port, the SBUF will pop out the 
 most top data in buffer when each time you read it.
 