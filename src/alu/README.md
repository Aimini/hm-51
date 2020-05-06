# Introduction
This document is [ALUS](#ALUS) and [ALUD](#ALUD) function descrption.

# ALUS
## input and output
ALUS is a single operand ALU, it have 3 part inputs, a 8-bit operand `A`, a 1-bit operand `C`, and a function select input `S`.
It have one ouput `Q`.

## encoding
The number in first column are the upper nibble, the number in fisrt row  are the lower nibble.

|encode|0|1|2|3|
|:-:|:-:|:-:|:-:|:-:|
|0|[ADJF](###0.-ADJF)|[IVADDR](###1.-IVADDR)|[CAA](###2.-CAA)|[SFR](###3.-SFR)|
|1|[RR](###4.-RR)|[RL](###5.-RL)|[RRC](###6.-RRC)|[RLC](###7.-RLC)|
|2|[INC](###8.-INC)|[DEC](###9.-DEC)|[BADDR](###10.-BADDR)|[BIDX](###11.-BIDX)|
|3|[SETCY](###12.-SETCY)|[SELHIRQ](###13.-SELHIRQ)|[ISRRETI](###14.-ISRIRETI)|[SWAP](###15.-SWAP)|

## Description
### 0. ADJF

Swap `A[6]` and `A[3]`.

|7|6    |5-4 |3  |2-0|
|:-:|:-:  |:-: |:-:|:-:|
|A\[7\]|A\[3\]|A\[5:4\]|A\[6\]|A\[2:0\]|

Usage:

See function [SETPSWF](####9.-SETPSWF) to know how this example work.
``` python
# ADDC example
RF(T0,WE), ALU(ADDCF), BUS(ALU)     # T0 + WR, store flag to T0, CY at A[7], OV at A[6], AC at A[3]
RF(T0), ALU(ADJF), BUS(ALU), WR(WE) # now OV at A[3], AC at A[6]
RF(PSW, WE), ALU(SETPSWF), BUS(ALU) 
```
See function [DA](####1.-DA) to know how this example work.
``` python
# DA example
RF(PSW), ALU(ADJF), BUS(ALU), WR(WE) # now AC at A[3], CY still at A[7].
RF(A, WE), ALU(DA), BUS(ALU) 
```

### 1. IVADDR
Get interrupt vector address from IRQ number.

|7-0|
|:-:|
|((A & 3) << 3) + 3|


### 2. CAA

`C` logic and with each bit in `A`.

|7|6|5|4|3|2|1|0|
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
|C&A\[7\]|C&A\[6\]|C&A\[5\]|C&A\[4\]|C&A\[3\]|C&A\[2\]|C&A\[1\]|C&A\[0\]|

### 3. SFR
Get register number in the RF from SFR address.

|7-5|4|3-0|
|:-:|:-:|:-:|
|0|SFR hit|SFR number in RF|

 For example, if RF\[1\] is register B,
 and we know B's SFR address is 0xF0. When input `A` is 0xF0, the `Q[4]`(SFR hit) is 1, and `Q[3:0]` is 1. If `A` is address without SFR mapped, the `Q[4]`(SFR hit) is 0, `Q[3:0]` can be any arbitrary number.


### 4. RR
Rotate shift right `A`.
|7|6|5|4|3|2|1|0|
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
|A\[0\]|A\[7\]|A\[6\]|A\[5\]|A\[4\]|A\[3\]|A\[2\]|A\[1\]|

### 5. RL
Rotate shift left `A`.
|7|6|5|4|3|2|1|0|
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
|A\[6\]|A\[5\]|A\[4\]|A\[3\]|A\[2\]|A\[1\]|A\[0\]|A\[7\]|

### 6. RRC
Rotate shift right `A` with C.
|7|6|5|4|3|2|1|0|
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
|C|A\[7\]|A\[6\]|A\[5\]|A\[4\]|A\[3\]|A\[2\]|A\[1\]|

### 7. RLC
Rotate shift left `A` with C.
|7|6|5|4|3|2|1|0|
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
|A\[6\]|A\[5\]|A\[4\]|A\[3\]|A\[2\]|A\[1\]|A\[0\]|C|


### 8. INC
`Q` = `A` + 1
|7-0|
|:-:|
|A + 1|


### 9. DEC
`Q` = `A` - 1
|7-0|
|:-:|
|A - 1|

### 10. BADDR
Get direct address from bit address.

|7-0|
|:-:|
|A < 0x80 ? A >> 3 : A & 0xF8|

8051 have bit-addressable ram region, In short, for addresses less than 0x80, the direct address is 0x20 + (`A` >> 3), and for addresses that greater than or equal to 0x80, the direct addresses is `A` & 0xF8.

### 11. BIDX
 Get **b**it **i**n**d**e**x** of target byte from bit address.


 |7-4|3-0|
 |:-:|:-:|
 |A & 0x7|A & 0x7|

 For 8051, it's always lower 3-bit of the bit address. it's usually work with BADDR. To facilitate the implementation of [INSB](####6.-INSB) and [EXTB](####7.-EXTB) functions in ALUD, the target index is in both low nibble and high nibble.


### 12. SETCY
 set `A[7]` to `C`.

 |7|6-0|
 |:-:|:-:|
 |C|A\[6:0\]|

 It's usually used to **set** PSW's **CY** flag. It's work for instruction that only affected CY flag(SETB C, DA A, CPL C, etc..)
 
### 13. SELHIRQ
(TODO)

### 14. ISRRETI
(TODO)


### 15. SWAP
**Swap** the nibble within the `A`.

|7-4|3-0|
|:-:|:-:|
|A\[3:0\]|A\[7:4\]|


# ALUD
## Input and output
ALUD is a double operands ALU, it have four part inputs, two 4-bit operand `A``B`,  and a function select input `S`, a 1-bit operand `C`.
It have two  4-bit ouput `LQ` and `HQ`.

```python
    ╔══════════╗
  ┌ ╢A0        ║
  │ ╢.         ║
A ┥ ╢.       D0╠ ┐
  └ ╢.   A    .╠ │
  ┌ ╢.   T    .╠ ├ LQ
  │ ╢.   2    .╠ ┘
B ┥ ╢.   8    .╠ ┐
  └ ╢.   C    .╠ │
  ┌ ╢.   6    .╠ ├ HQ
  │ ╢.   4   D7╠ ┘
S ┥ ╢.         ║
  └ ╢.         ║
C ─ ╢A12       ║
    ╚══════════╝
```

Obviously,a single chip can't encoding function that contain two 8-bit inputs with and an 8-bit output, but we can combine two chip togther. For function like `AND` `OR`, they don't need info from low part, lower nibble and high nibble can calculate indvidually and then combine the output to one 8-bit output. For one chip, a function only using 4-bit ouput, and we can using another 4-bit to encoding other function, for example, we can encode `AND` and `OR` in the same `S` input:

```python
   ╔══════════╗
A ─╢   AT28   ║
B ─╢   C64    ╟─ LQ: A or B
S ─╢          ╟─ HQ: A and B
C ─╢          ║
   ╚══════════╝
```
So forth, combine two chip we can get:
```python
    ╔══════════╗
AL ─╢   AT28   ║
BL ─╢   C64  LQ╟─────┯━━━━━  LQ
S  ─╢        HQ╟─────┼─┐
C0 ─╢          ║     │ │
    ╚══════════╝     │ │
                     │ │ 
    ╔══════════╗     │ │
AH ─╢   AT28   ║     │ │
BH ─╢   C64  LQ╟─────┘ │
S  ─╢        HQ╟───────┷━━━  HQ
C1 ─╢          ║
    ╚══════════╝
```

But for function like `ADD`, `SUB`, the need carry signal from low part, we need some ouput to perform carry out ouput. In my design, HQ was used as carry out ouput(although carry out need only 1 bit), so one `S` can only encode one function for these case:
```python
      ╔══════════╗
    ┌ ╢A0        ║
    │ ╢.         ║
 AL ┥ ╢.       D0╟ ┐
    └ ╢.   A    .╟ │
    ┌ ╢.   T    .╟ ├ AL + BL
    │ ╢.   2    .╟ ┘
 BL ┥ ╢.   8    .╟ 
    └ ╢.   C    .╟ 
    ┌ ╢.   6    .╟        CY
    │ ╢.   4   D7╟────────┴─────┐
  S ┥ ╢.         ║              │
    └ ╢.         ║              │
  C ─ ╢A12       ║              │
      ╚══════════╝              │
                                │
      ╔══════════╗              │
    ┌ ╢A0        ║              │
    │ ╢.         ║              │
 AH ┥ ╢.       D0╟ ┐            │
    └ ╢.   A    .╟ │            │
    ┌ ╢.   T    .╟ ├ AH + BH    │
    │ ╢.   2    .╟ ┘            │
 BH ┥ ╢.   8    .╟              │
    └ ╢.   C    .╟              │
    ┌ ╢.   6    .╟              │
    │ ╢.   4   D7╟ ─ CY         │
  S ┥ ╢.         ║              │
    └ ╢.         ║              │
  C┌──╢A12       ║              │
   │  ╚══════════╝              │
   └────────────────────────────┘
```


## Encoding
For convenient, we treat high part's `QL` and low part's `QL` to one 8-bit `QL` output, and `QH` so on. We will explain it separately if necessary.

The number in first column is the upper nibble in `S`, the number in fisrt row is the lower nibble in `S`.

 **QL:**

|encode|0|1|2|3|
|:-:|:-:|:-:|:-:|:-:|
|0|[XOR](####0.-XOR)|[DA](####1.-DA)|[ADDC](####2.-ADDC)|[SUBB](####3.-SUBB)|
|1|[A](####4.-A)|[Ri](####5.-Ri)|[INSB](####6.-INSB)|[XCHD](####7.-XCHD)|
|2|[GENIRQN](####8.-GENIRQN)|[SETPSWF](####9.-SETPSWF)|[ADDR11REPLACE](####10.-ADDR11REPLACE)|[SETOVCLRCY](####11.-SETOVCLRCY)|
|3|[B](####12.-B)|[Rn](####13.-Rn)|[SETPF](####14.-SETPF)|[INCC](####15.-INCC)|

**QH:**

|encode|0|1|2|3|
|:-:|:-:|:-:|:-:|:-:|
|0|[CPLB](####0.-CPLB)|[DAF](####1.-DAF)|[ADDCF](####2.-ADDCF)|[SUBBF](####3.-SUBBF)|
|1|[PF](####4.-PF)|[OR](####5.-OR)|[INSBF](####6.-INSBF)|[EXTB](####7.-EXTB)|
|2|[ISRAPPIRQ](####8.-ISRAPPIRQ)|[ZF](####9.-ZF)|||
|3|[ZF_B](####12.-ZF_B)|[AND](####13.-AND)|[NA](####14.-NA)|[INCCF](####15.-INCCF)|

## Description

### QL
Remember, QL is consist of low part chip's low nibble and high part chip's low nibble.

#### 0. XOR
`QL` equal to `A` logic xor `B`.

 |7-0|
 |:-:|
 |A ^ B|

#### 1. DA

See instruction `DA A` to get detail. 

 |7-0|
 |:-:|
 |DA(A,B)|

We treat `B[3]` as `AC`, `B[7]` ac `CY`, according to instruction set manual, it's essentially to perform two step conditional addition using to `A`. First additionneed to using `AC` flag, but it's in low part chip, that's why `CY` must at `B[3]` to `B[0]` rather than in original position `PSW[6]`(see [ADJF](###0.-ADJF) to know how could we transform `PSW` to `B` that used by this function). Second is in high part, so it's need output a carry signal, `AC` flag don't need to change position but need using carry signal from low part, so it's must work together with function [DAF](####1.-DAF).
#### 2. ADDC

 `QL` = `A` + `B` + `C`.

 |7-0|
 |:-:|
 |A + B + C|

 Need output carry signal from low part chip to high part chip, see [ADDCF](####2.-ADDCF).

### 3. SUBB

 `QL` = `A` - `B` - `C`.

 |7-0|
 |:-:|
 |A - B - C|

 Need output borrow signal from low part chip to high part chip, see [ADDCF](####2.-ADDCF).

#### 4. A

`QL` = `A`.

 |7-0|
 |:-:|
 |A|


#### 5. Ri
`Q = (A & 0x18) | (B & 0x1)`.

 |7-5|4  |3  |2  |1-0|
 |:-:|:-:|:-:|:-:|:-:|
 |0|A\[4\]|A\[3\]|0|B\[1:0\]|

 It's used to generate register bank address when using indirect address. Under normal circumstances, `A = PSW`, `B = IR`.
 ``` python
 #example
 RF(IR), ALU(A), WR(WE)
 RF(PSW), ALU(Ri), SR(WE) # load to SR as ram address
 BUS(RAM)                 # do something with @Ri value
 ```

#### 6. INSB
Let `T = A`, Then let `T[B[2:0]] = C`, then `Q = T`.
|7|6|5|4|3|2|1|0|
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
|B\[2:0\] == 7 ? C : A\[7\]|B\[2:0\] == 6 ? C : A\[6\]|B\[2:0\] == 5 ? C : A\[5\]|B\[2:0\] == 4 ? C : A\[4\]|B\[2:0\] == 3 ? C : A\[3\]|B\[2:0\] == 2 ? C : A\[2\]|B\[2:0\] == 1 ? C : A\[1\]|B\[2:0\] == 0 ? C : A\[0\]|


#### 7. XCHD

#### 8. GENIRQN
  

#### 9. SETPSWF
 Replace `A[7]` to `B[7]`, `A[6]` to `B[6]`, `A[2]` to `B[3]`.

 |7|6|5|4|3|2|1|0|
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
|A\[7\]|B\[6\]|A\[5\]|A\[4\]|A\[3\]|B\[3\]|A\[1\]|A\[0\]|

It's usually used to set PSW flag when execute `ADDC`,`SUBB`,`ADD` instruction. See [ADJF](###0.-ADJF) to know how to use this function.

#### 10. ADDR11REPLACE
`A[2:0]` = `B[3:1]`

 |7-3|2-0|
 |:-:|:-:|
 |A\[7:3\]|B\[3:1\]|

This function was used to `AJMP` and `ACALL`, let's explain how it work. In ISA, the abs address is a 11bit immed:

|encoding|byte0    |  byte1 |
|:-:     |:-:        |:-:|
|value|A10-A8 xxxxx|A7-A0|

And when excute `AJMP` and `ACALL` we have a step `PC[10:0]= A[10:0]`, note `PC[15:8]` as `PCH`, `PC[7:0]` as `PCL`, then we get `PCL = A[7:0] = byte1` it's simply move `byte1` to `PCL`. For `PCH`, we have `PCH[2:0] = A[10:8]`,  meaing we want `PCH[2:0]` = `byte0[7:5]`. That's seem can't work by this function, but if excute [SWAP](###15.-SWAP) to `byte0`, we have `_byte0[3:0] = byte0[7:4]`, it's meaing `_byte0[3:1] = byte0[7:5]`, and now, we can excute `ADDR11REPLACE`.

```  python
# example
RF(IR), ALU(SWAP), WR(WE)        # move ADDR11[10:8] to WR[3:1]
RF(PCH,WE), ALU(ADDR11REPLACE)
```


#### 13. Rn
`Q = (A & 0x18) | (B & 0x7)`.

 |7-5|4  |3  |2  |1-0|
 |:-:|:-:|:-:|:-:|:-:|
 |0|A\[4\]|A\[3\]|0|B\[1:0\]|

 Similar to function `Ri`, it's used to generate register bank address when using Rn address. Under normal circumstances, `A = PSW`, `B = IR`.

 ``` python
 #example
 RF(IR), ALU(A), WR(WE)
 RF(PSW), ALU(Rn), SR(WE) # load to SR as ram address
 BUS(RAM)                 # do something with Rn value
 ```

#### 14. SETPF
 replace `A[0]` to `C`.
 |7-1 |0|
 |:-:|:-:|
 |A\[7:1\] |C |

Use to set parity flag in `PSW`.


#### 15. INCC
`Q` = `A` + `C`.

|7-0|
 |:-:|
 |A + C|
 Obviously, it's need generate carry ouput, see [INCCF](####15.-INCCF).

___
### QH
#### 0. CPLB
 (TODO)

#### 1. DAF

If there a carry from low nibble, `AC` is 1, if there a carry from high nibble, `CY` is 1.
 |7  |6-4|3  |2-0|
 |:-:|:-:|:-:|:-:|
 |CY |X  |AC |X  |

#### 2. ADDCF
If there a carry from low nibble, `AC` is 1, if there a carry from high nibble, `CY` is 1. if the result of `ADDC` is overflow, `OV` is 1.
 |7  |6  |5-4|3  |2-0|
 |:-:|:-:|:-:|:-:|:-:|
 |CY |OV | X |AC | X |

#### 3. SUBBF
If there a borrow from low nibble, `AC` is 1, if there a borrow from high nibble, `CY` is 1. if the result of `SUBB` is overflow, `OV` is 1.
 |7  |6  |5-4|3  |2-0|
 |:-:|:-:|:-:|:-:|:-:|
 |CY |OV | X |AC | X |

#### 4. PF
if `A[3:0]` contains an odd number of 1s, then `PFL` is 1, if `A` contains an odd number of 1s, then `PF` is 1.

|7|6-4|3|2-0|
|:-:|:-:|:-:|:-:|
|PF|X|PFL|X|


#### 5. OR
`QL` equal to `A` logic or `B`. 

 |7-0|
 |:-:|
 |A \| B|

#### 6. INSBF
(TODO)
#### 7. EXTB
`Q[7] = A[B[2:0]]`.
|7|6-4|3|2-0|
|:-:|:-:|:-:|:-:|
|A\[B\[2:0\]\]|X|B\[2:0\] < 4 ? A\[B\[2:0\]\] : 0|X|

Let see how it work.

Usually, the B is the result of [BIDX](###11.-BIDX), so `B[2:0]` and `B[6:4]` is the same value, they are both the bit index. 

In low part, `B[2:0] < 4` meaing the bix you want get is in `A[3:0]`, we get the bit from it, but the final output of bit is in `Q[7]`, so we need send the bit from low part chip to high part chip, which what you see at `Q[3]`.

In high part, `B[2:0] < 4` meaing the bix you want get is in low part, so we set the `Q[7]` to the value of `C`. But if `B[2:0] >= 4`, we take bit from `A[7:4]` as output.

#### 9. ZF
if `A[3:0] == 0`, then `ZFL = 1`. If `A` is 0, then `ZF` is 1.

|7|6-4|3|2-0|
|:-:|:-:|:-:|:-:|
|ZF|X|ZFL|X|

#### 12. ZF_B
(TODO)


#### 13. AND
`QL` equal to `A` logic and `B`.

 |7-0|
 |:-:|
 |A & B|


#### 14. NA
`Q` equal to logic not `A`.

 |7-0|
 |:-:|
 |~A|


#### 15. INCCF
If there a carry from low nibble, `AC` is 1, if there a carry from high nibble, `CY` is 1.

 |7  |6  |5-4|3  |2-0|
 |:-:|:-:|:-:|:-:|:-:|
 |CY |X  | X |AC | X |


