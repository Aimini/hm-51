# Table of Content <!-- omit in toc -->
- [Introduction](#introduction)
- [Encode Constraints](#encode-constraints)
- [ALUS](#alus)
  - [input and output](#input-and-output)
  - [encoding](#encoding)
  - [Description](#description)
- [ALUD](#alud)
  - [Input and output](#input-and-output-1)
  - [Encoding](#encoding-1)
  - [Description](#description-1)


# Introduction

This document contains descriptions of [ALUS](#ALUS) and [ALUD](#ALUD) functions.

# Encode Constraints
  For flag type (`ADDCF`, `SUBBF`, etc.) functions, we put it at ALUD-H naturally.
  Nonetheless, due to some hardware trick,
  there are some constraints for encoding some functions:

  - `B`/`ZF_B`/`SETCY` must have same encoding, `ZF_B` shoud encoded at ALUD-H.
  - `OR` shoud encoded at ALUD-H.

# ALUS

## input and output

ALUS is a single-operand ALU, which have 3  inputs and 1 output.

It contains an 8-bit operand input, denoted as `A` , a 1-bit operand `C` and a 4-bit function selection input `S` .

 It has an 8-bit output `Q` .

## encoding

The number in first column are the upper nibble, the number in fisrt row  are the lower nibble.

| encode |         0          |             1              |           2            |        3         |
|:------:|:------------------:|:--------------------------:|:----------------------:|:----------------:|
|   0    |  [ADJF](#0-adjf)   |    [IVADDR](#1-ivaddr)     |     [CAA](#2-caa)      |  [SFR](#3-sfr)   |
|   1    |    [RR](#4-rr)     |        [RL](#5-rl)         |     [RRC](#6-rrc)      |  [RLC](#7-rlc)   |
|   2    |   [INC](#8-inc)    |       [DEC](#9-dec)        |   [BADDR](#10-baddr)   | [BIDX](#11-bidx) |
|   3    | [SETCY](#12-setcy) | [SELHIRRQN](#13-selhirrqn) | [ISRRETI](#14-isrreti) | [SWAP](#15-swap) |

## Description

### 0. ADJF

Swap `A[6]` and `A[3]` .

|   7    | 6      | 5-4      |   3    |   2-0    |
|:------:|:-------|:---------|:------:|:--------:|
| A\[7\] | A\[3\] | A\[5:4\] | A\[6\] | A\[2:0\] |

Usage:

See function [SETPSWF](#9-setpswf) to know how this example work.

``` python
# ADDC example
RF(T0,WE), ALU(ADDCF), BUS(ALU)     # T0 + WR, store flag to T0, CY at A[7], OV at A[6], AC at A[3]
RF(T0), ALU(ADJF), BUS(ALU), WR(WE) # now OV at A[3], AC at A[6]
RF(PSW, WE), ALU(SETPSWF), BUS(ALU)
```

See function [DA](#1-da) to know how this example work.

``` python
# DA example
RF(PSW), ALU(ADJF), BUS(ALU), WR(WE) # now AC at A[3], CY still at A[7].
RF(A, WE), ALU(DA), BUS(ALU)
```

### 1. IVADDR

Get interrupt vector address according to IRQ number.

|        7-0         |
|:------------------:|
| ((A & 3) << 3) + 3 |

### 2. CAA

Each bit in `A` and `C` performs logical AND operation.

|    7     |    6     |    5     |    4     |    3     |    2     |    1     |    0     |
|:--------:|:--------:|:--------:|:--------:|:--------:|:--------:|:--------:|:--------:|
| C&A\[7\] | C&A\[6\] | C&A\[5\] | C&A\[4\] | C&A\[3\] | C&A\[2\] | C&A\[1\] | C&A\[0\] |

### 3. SFR

Obtain the SFR number in RF according to the SFR address.

| 7-5 |    4    |       3-0        |
|:---:|:-------:|:----------------:|
|  0  | SFR hit | SFR number in RF |

 For example, if RF\[1\] is register B, and we know that B's SFR address is 0xF0. When input `A` is 0xF0, the `Q[4]` (SFR hit) is 1, and `Q[3:0]` is 1. If `A` is an address without SFR mapped, the `Q[4]` (SFR hit) is 0, `Q[3:0]` can be any arbitrary number.

### 4. RR

Rotate shift right `A` .
|   7    |   6    |   5    |   4    |   3    |   2    |   1    |   0    |
|:------:|:------:|:------:|:------:|:------:|:------:|:------:|:------:|
| A\[0\] | A\[7\] | A\[6\] | A\[5\] | A\[4\] | A\[3\] | A\[2\] | A\[1\] |

### 5. RL

Rotate shift left `A` .
|   7    |   6    |   5    |   4    |   3    |   2    |   1    |   0    |
|:------:|:------:|:------:|:------:|:------:|:------:|:------:|:------:|
| A\[6\] | A\[5\] | A\[4\] | A\[3\] | A\[2\] | A\[1\] | A\[0\] | A\[7\] |

### 6. RRC

Rotate shift right `A` with `C` .
| 7 |   6    |   5    |   4    |   3    |   2    |   1    |   0    |
|:-:|:------:|:------:|:------:|:------:|:------:|:------:|:------:|
| C | A\[7\] | A\[6\] | A\[5\] | A\[4\] | A\[3\] | A\[2\] | A\[1\] |

### 7. RLC

Rotate shift left `A` with `C` .
|   7    |   6    |   5    |   4    |   3    |   2    |   1    | 0 |
|:------:|:------:|:------:|:------:|:------:|:------:|:------:|:-:|
| A\[6\] | A\[5\] | A\[4\] | A\[3\] | A\[2\] | A\[1\] | A\[0\] | C |

### 8. INC

`Q = A + 1` .
|  7-0  |
|:-----:|
| A + 1 |

### 9. DEC

`Q = A - 1` .
|  7-0  |
|:-----:|
| A - 1 |

### 10. BADDR

Get bytes's direct address according bit address.

|             7-0              |
|:----------------------------:|
| A < 0x80 ? A >> 3 : A & 0xF8 |

 8051 have bit-addressable ram region.
 In short, for addresses less than 0x80, the direct address is 0x20 + ( `A` >> 3), and for addresses that greater than or equal to 0x80, the direct addresses is `A` & 0xF8.

### 11. BIDX

 Get the target bit index in the target byte  from the byte address.

|   7-4   |   3-0   |
|:-------:|:-------:|
| A & 0x7 | A & 0x7 |

 For 8051, it's always lower 3-bit of the bit address. it's usually work with [BADDR](#10-baddr). To facilitate the implementation of [INSB](#6-insb) and [EXTB](#7-extb) functions in ALUD, the target index is in both low nibble and high nibble.

### 12. SETCY

 set `A[7]` to `C` .

| 7 |   6-0    |
|:-:|:--------:|
| C | A\[6:0\] |

 It's usually used to **set** PSW's **CY** flag. It's work for instruction that only affected CY flag(SETB C, DA A, CPL C, etc.)

### 13. SELHIRRQN

 Select the highest priority interrupt(not the interrupt number) from the input `A` .

 In short, you must using function [GENIRRQN](#8-genirrqn) to get the IRQ Number, IRQ flag and the IP flag, then using `SELHIRRQN` to get highest IRQ number and `IP` flag.

| 7  | 6-3 | 2-0  |
|:--:|:---:|:----:|
| IP |     | IRQN |

``` python
 #example
 RF(IP),  ALU(A), WR(WE) # WR <- IP
 RF(T0,WE), BUS(IRR)     # T0 <- IRQ
 RF(T0,WE), ALU(GENIRRQN) # T0 <- generate IRQ number, IP flag, interrupt valid flag.
 RF(T0,WE), ALU(SELHIRRQN) # T0 <- get highest interrupt request and IP flag.

 RF(T0), ALU(GENIRRQN), WR(WE), JLT(0x1, STAGE_FETCH)
 RF(ISR, WE), ALU(ISRSET), IRR(CLR)
 RF(ISR), JGT(0x7F, STAGE_FETCH)
```

### 14. ISRRETI

 Clear the interrupt service flag in ISR, used in `RETI` instruction.
 See `Architecture Design` in /README.md to get more detail.

|   7    |            6             |            5             |   4-0    |
|:------:|:------------------------:|:------------------------:|:--------:|
| A\[7\] | A\[6\] == 1 ? 0 : A\[6\] | A\[6\] == 0 ? 0 : A\[5\] | A\[4:0\] |

### 15. SWAP

**Swap** the nibble within the `A` .

|   7-4    |   3-0    |
|:--------:|:--------:|
| A\[3:0\] | A\[7:4\] |

# ALUD

## Input and output

ALUD is a double operands ALU, it have four part inputs, two 4-bit operand `A`  `B` , and a function select input `S` , a 1-bit operand `C` .
It have two  4-bit output `LQ` and `HQ` .

``` python
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

Obviously, a single chip can't encoding function that contain two 8-bit inputs with and an 8-bit output, but we can combine two chip togther. For function like `AND`  `OR` , they don't need info from low part, lower nibble and high nibble can calculate indvidually and then combine the output to one 8-bit output. For one chip, a function only using 4-bit output, and we can using another 4-bit to encoding other function, for example, we can encode `AND` and `OR` in the same `S` input:

``` python
   ╔══════════╗
A ─╢   AT28   ║
B ─╢   C64    ╟─ LQ: A or B
S ─╢          ╟─ HQ: A and B
C ─╢          ║
   ╚══════════╝
```

So forth, combine two chip we can get:

``` python
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

But for function like `ADD` , `SUB` , the need carry signal from low part, we need some output to perform carry out output. In my design, HQ was used as carry out output(although carry out need only 1 bit), so one `S` can only encode one function for these case:

``` python
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

The number in first column is the upper nibble in `S` , the number in fisrt row is the lower nibble in `S` .

 **QL:**

| encode |            0            |           1           |                 2                  |              3               |
|:------:|:-----------------------:|:---------------------:|:----------------------------------:|:----------------------------:|
|   0    |      [XOR](#0-xor)      |      [DA](#1-da)      |          [ADDC](#2-addc)           |       [SUBB](#3-subb)        |
|   1    |        [A](#4-a)        |      [Ri](#5-ri)      |          [INSB](#6-insb)           |       [XCHD](#7-xchd)        |
|   2    | [GENIRRQN](#8-genirrqn) | [SETPSWF](#9-setpswf) | [ADDR11REPLACE](#10-addr11replace) | [SETOVCLRCY](#11-setovclrcy) |
|   3    |       [B](#12-b)        |     [Rn](#13-rn)      |         [SETPF](#14-setpf)         |       [INCC](#15-incc)       |

**QH:**

| encode |          0          |       1        |         2         |         3          |
|:------:|:-------------------:|:--------------:|:-----------------:|:------------------:|
|   0    |   [CPLB](#0-cplb)   | [DAF](#1-daf)  | [ADDCF](#2-addcf) | [SUBBF](#3-subbf)  |
|   1    |     [PF](#4-pf)     |  [OR](#5-or)   | [INSBF](#6-insbf) |  [EXTB](#7-extb)   |
|   2    | [ISRSET](#8-isrset) |  [ZF](#9-zf)   |   [NA](#10-na)    |                    |
|   3    |  [ZF_B](#12-zf_b)   | [AND](#13-and) |    [(NONE)](#14-none) | [INCCF](#15-inccf) |

## Description

### QL

Remember, QL is consist of low part chip's low nibble and high part chip's low nibble.

#### 0. XOR

`QL` equal to `A` logic xor `B` .

|  7-0  |
|:-----:|
| A ^ B |

#### 1. DA

See instruction `DA A` to get detail. 

|   7-0    |
|:--------:|
| DA(A, B) |

We treat `B[3]` as `AC` , `B[7]` ac `CY` , according to instruction set manual, it's essentially to perform two step conditional addition using to `A` . First additionneed to using `AC` flag, but it's in low part chip, that's why `CY` must at `B[3]` to `B[0]` rather than in original position `PSW[6]` (see [ADJF](#0-adjf) to know how could we transform `PSW` to `B` that used by this function). Second is in high part, so it's need output a carry signal, `AC` flag don't need to change position but need using carry signal from low part, so it's must work together with function [DAF](#1-daf).

#### 2. ADDC

`QL` = `A` + `B` + `C` .

|    7-0    |
|:---------:|
| A + B + C |

 Need output carry signal from low part chip to high part chip, see [ADDCF](#2-addcf).

#### 3. SUBB

`QL` = `A` - `B` - `C` .

|    7-0    |
|:---------:|
| A - B - C |

 Need output borrow signal from low part chip to high part chip, see [ADDCF](#2-addcf).

#### 4. A

`QL` = `A` .

| 7-0 |
|:---:|
|  A  |

#### 5. Ri

`Q = (A & 0x18) | (B & 0x1)` .

| 7-5 |   4-3    | 2-1 |   0    |
|:---:|:--------:|:---:|:------:|
|  0  | A\[4:3\] |  0  | B\[0\] |

 It's used to generate register bank address when using indirect address. Under normal circumstances, `A = IR` , `B = PSW` .

``` python
 #example
 RF(PSW), ALU(A), WR(WE)
 RF(IR), ALU(Ri), SR(WE) # load to SR as ram address
 BUS(RAM)                 # do something with @Ri addr value
 ```

#### 6. INSB

Let `T = A` , Then let `T[B[2:0]] = C` , then `Q = T` .
|             7              |             6              |             5              |             4              |             3              |             2              |             1              |             0              |
|:--------------------------:|:--------------------------:|:--------------------------:|:--------------------------:|:--------------------------:|:--------------------------:|:--------------------------:|:--------------------------:|
| B\[2:0\] == 7 ? C : A\[7\] | B\[2:0\] == 6 ? C : A\[6\] | B\[2:0\] == 5 ? C : A\[5\] | B\[2:0\] == 4 ? C : A\[4\] | B\[2:0\] == 3 ? C : A\[3\] | B\[2:0\] == 2 ? C : A\[2\] | B\[2:0\] == 1 ? C : A\[1\] | B\[2:0\] == 0 ? C : A\[0\] |

Because the high part output must using `C` when B\[2:0\] >= 4, then we have function [INSBF](#6-insbf) to do this stuff.

#### 7. XCHD

`Q = {A[7:4],B[3:0]}` .
Concat the high nibble of `A` and the low nibble of `B` .

|   7-4    |   3-0    |
|:--------:|:--------:|
| A\[7:4\] | B\[3:0\] |

``` python
# example: swap low nibble of T0 and low nibble of T1
RF(T0), ALU(A), WR(WE)
RF(T2,WE), ALU(B)        # backup, T2 <- T0
RF(T1), ALU(A), WR(WE)
RF(T0,WE), ALU(XCHD)  # {T0[7:4], T1[3:0]}
RF(T2), ALU(A), WR(WE)
RF(T1,WE), ALU(XCHD)
```

#### 8. GENIRRQN

 Select the highest priority interrupt number in the high nibble and low nibble  respectively.

 See example in [SELHIRRQN](#13-selhirrqn).

| 7  | 6  | 5-4  | 3  | 2  | 1-0  |
|:--:|:--:|:----:|:--:|:--:|:----:|
| IV | IP | IRQn | IV | IP | IRQn |
| H  | H  |  H   | L  | L  |  L   |

 The `A` must be IRQ and `B` must be thevalue  of `IP` .

 IV: interrupt valid flag. If there is any IRQ in this nibble, this flag is 1, otherwise it is 0.

 IP: IP flag. If the corresponding bit of the high priority interrupt in the `IP` register is 1, then this flag is 1, otherwise it is 0.

 IRQn: the highest priority interrupt number.

#### 9. SETPSWF

 Replace `A[7]` to `B[7]` , `A[6]` to `B[6]` , `A[2]` to `B[3]` .

|   7    |   6    |   5    |   4    |   3    |   2    |   1    |   0    |
|:------:|:------:|:------:|:------:|:------:|:------:|:------:|:------:|
| B\[7\] | B\[6\] | A\[5\] | A\[4\] | A\[3\] | B\[3\] | A\[1\] | A\[0\] |

It's usually used to set PSW flag when execute `ADDC` , `SUBB` , `ADD` instruction. See [ADJF](#0-adjf) to know how to use this function.

#### 10. ADDR11REPLACE

`A[2:0]` = `B[3:1]`.

|   7-3    |   2-0    |
|:--------:|:--------:|
| A\[7:3\] | B\[3:1\] |

This function was used to `AJMP` and `ACALL` , let's explain how it work. In ISA, the abs address is a 11bit immed:

| encoding | byte0        | byte1 |
|:---------|:-------------|:------|
| value    | A10-A8 xxxxx | A7-A0 |

And when excute `AJMP` and `ACALL` we have a step `PC[10:0]= A[10:0]` , note `PC[15:8]` as `PCH` , `PC[7:0]` as `PCL` , then we get `PCL = A[7:0] = byte1` it's simply move `byte1` to `PCL` . For `PCH` , we have `PCH[2:0] = A[10:8]` , meaing we want `PCH[2:0]` = `byte0[7:5]` . That's seem can't work by this function, but if excute [SWAP](#15-swap) to `byte0` , we have `_byte0[3:0] = byte0[7:4]` , it's meaing `_byte0[3:1] = byte0[7:5]` , and now, we can excute `ADDR11REPLACE` .

``` python
# example
RF(IR), ALU(SWAP), WR(WE)        # move ADDR11[10:8] to WR[3:1]
RF(PCH,WE), ALU(ADDR11REPLACE)
```

#### 13. Rn

`Q = (A & 0x18) | (B & 0x7)` .

| 7-5 |   4-3    |   2-0    |
|:---:|:--------:|:--------:|
|  0  | B\[4:3\] | A\[2:0\] |

 Similar to function `Ri` , it's used to generate register bank address when using Rn address. Under normal circumstances, `A = IR` , `B = PSW` .

``` python
 #example
 RF(PSW), ALU(A), WR(WE)
 RF(IR), ALU(Rn), SR(WE) # load to SR as ram address
 BUS(RAM)                 # do something with Rn value
 ```

#### 14. SETPF

 replace `A[0]` to `C` .

|   7-1    | 0 |
|:--------:|:-:|
| A\[7:1\] | C |

Use to set parity flag in `PSW` .

#### 15. INCC

`Q` = `A` + `C` .

|  7-0  |
|:-----:|
| A + C |

 Obviously, it's need generate carry output, see [INCCF](#15-inccf).

___

### QH

#### 0. CPLB

 using `A` as bit index, invert(complement) the bit in `B` .

``` python
Q = B
Q[A[2:0]] = ~Q[A[2:0]]
```

|7-0|
|:-:|:-:|:-:|:-:|
|CPLB(A, B)|

 The `A` must be the result of [BIDX](#11-bidx).

#### 1. DAF

If there a carry from low nibble, `AC` is 1, if there a carry from high nibble, `CY` is 1.

| 7  | 6-4 | 3  | 2-0 |
|:--:|:---:|:--:|:---:|
| CY |  X  | AC |  X  |

#### 2. ADDCF

If there a carry from low nibble, `AC` is 1, if there a carry from high nibble, `CY` is 1. if the result of `ADDC` is overflow, `OV` is 1.

| 7  | 6  | 5-4 | 3  | 2-0 |
|:--:|:--:|:---:|:--:|:---:|
| CY | OV |  X  | AC |  X  |

#### 3. SUBBF

If there a borrow from low nibble, `AC` is 1, if there a borrow from high nibble, `CY` is 1. if the result of `SUBB` is overflow, `OV` is 1.

| 7  | 6  | 5-4 | 3  | 2-0 |
|:--:|:--:|:---:|:--:|:---:|
| CY | OV |  X  | AC |  X  |

#### 4. PF

if `A[3:0]` contains an odd number of 1s, then `PFL` is 1, if `A` contains an odd number of 1s, then `PF` is 1.

| 7  | 6-4 |  3  | 2-0 |
|:--:|:---:|:---:|:---:|
| PF |  X  | PFL |  X  |

#### 5. OR

`QL` equal to `A` logic or `B` .

|  7-0   |
|:------:|
| A \| B |

#### 6. INSBF

Cooperate with [INSB](#6-insb) function, it's simply transmit signal `C` from low part chip to high part chip.

| 7-4 | 3 | 2-0 |
|:---:|:-:|:---:|
|  X  | C |  X  |

#### 7. EXTB

`Q[7] = B[A[2:0]]` .
|       7       | 6-4 |                3                 | 2-0 |
|:-------------:|:---:|:--------------------------------:|:---:|
| B\[A\[2:0\]\] |  X  | A\[2:0\] < 4 ? B\[A\[2:0\]\] : 0 |  X  |

Let see how it work.

Usually, the A is the result of [BIDX](#11-bidx), so `A[2:0]` and `A[6:4]` is the same value, they are both the bit index.

In low part, `A[2:0] < 4` meaing the bit you want get is in `B[3:0]` , we get the bit from it, but the final output of bit is in `Q[7]` , so we need send the bit from low part chip to high part chip, which what you see at `Q[3]` .

In high part, `A[2:0] < 4` meaing the bit that you wanna get is in low part, so we set the `Q[7]` to the value of `C` . But if `A[2:0] >= 4` , we take bit from `B[7:4]` as output.

#### 8. ISRSET

 Mark the corresponding interrupt servicing flag in the `ISR` register.

 In short, if `ISR` **can** accept current interrupt, the  **`Q[7]` is 0(be careful!)** , otherwise the **`Q[7]` is 1**. Current IRQ number are stored in `ISR[2:0]` .

 It should work with [ISRRETI](#14-isrreti).

|     7-0      |
|:------------:|
| ISRSET(A, B) |

*notice*

`A` must be `ISR` . and `B` must be the result of `SELHIRRQN` (see example in [SELHIRRQN](#13-selhirrqn)).

*detail*

 Let's see how it work: The bit where the interrupt service flag in the ISR is arbitrarily selected by us, but according to my `Hardware encoding` in `/README.md` :

* `ISR[6] == 1` means an interrupt with priority 1 is being servced.
* `ISR[5] == 1` means an interrupt with priority 0 is being servced.
* `ISR[7]` can be customized.

 Now assume `A = ISR` , `B` is the result of `SELHIRRQN` , we first list the condition that can't accept current interrupt.

* `A[6] == 1` , means that the priority of the interrupt being serviced is 1. You cannot accept any other interrupts because 1 is the highest priority.
* `A[6] == 0 && A[5] == 1 && B[7] == 0` , means that only interrupt with priority 0 be serviced, but IRQ's priority is 0 too, we shouldn'taccept it.

Then, we use `Q[7]` to indicate whether we can accept the interrupt.

#### 9. ZF

if `A[3:0] == 0` , then `ZFL = 1` . If `A` is 0, then `ZF` is 1.

| 7  | 6-4 |  3  | 2-0 |
|:--:|:---:|:---:|:---:|
| ZF |  X  | ZFL |  X  |
#### 10. NA

`Q` equal to logic not `A` .

| 7-0 |
|:---:|
| ~A  |
#### 12. ZF_B

Same as [ZF](#9-zf), but using B as operand. If `B[3:0] == 0` , then `ZFL = 1` . If `B` is 0, then `ZF` is 1.

| 7  | 6-4 |  3  | 2-0 |
|:--:|:---:|:---:|:---:|
| ZF |  X  | ZFL |  X  |

#### 13. AND

`QL` equal to `A` logic and `B` .

|  7-0  |
|:-----:|
| A & B |

#### 14. NONE


#### 15. INCCF

If there a carry from low nibble, `AC` is 1, if there a carry from high nibble, `CY` is 1.

| 7  | 6 | 5-4 | 3  | 2-0 |
|:--:|:-:|:---:|:--:|:---:|
| CY | X |  X  | AC |  X  |
