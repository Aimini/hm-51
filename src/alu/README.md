# Introduction
This document is alus and alud function descrption.

# ALUS
## input and output
ALUS is a single operand ALU, it have 3 part inputs, a 8-bit operand `A`, a 1-bit operand `C`, and a function select input `S`.
It have one ouput `Q`.

## encoding
The number in first column are the upper nibble, the number in fisrt row  are the lower nibble.

|name|0|1|2|3|
|:-:|:-:|:-:|:-:|:-:|
|0|A|NA|CAA|SFR|
|1|RR|RL|RRC|RLC|
|2|INC|DEC|BADDR|BIDX|
|3|SETCY|SETOVCLRCY|CHIRQ|SWAP|

## Description
### 0. ADJF

Swap `A[6]` and `A[3]`.

|7-0|
|:-:|
|A|

Usage:
```
# ADDC example
RF(T0,WE), ALU(ADDCF), BUS(ALU)     # T0 + WR, store flag to T0, CY at A[7], OV at A[6], AC at A[3]
RF(T0), ALU(ADJF), BUS(ALU), WR(WE) # now OV at A[3], AC at A[6]
RF(PSW, WE), ALU(SETPSWF), BUS(ALU) 
```

```
# DA example
RF(PSW), ALU(ADJF), BUS(ALU), WR(WE) # now AC at A[3], CY still at A[7].
RF(A, WE), ALU(DA), BUS(ALU) 
```

### 1. IVADDR
get interrupt vector address from IRQ number.

|7-0|
|:-:|
|((A & 3) << 3) + 3|


### 2. CCA

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

 for 8051, it's always lower 3-bit of the bit address. it's usually work with BADDR. To facilitate the implementation of INS and EXT functions in ALUD, the target index is in both low nibble and high nibble.


### 12. SETCY
 set `A[7]` to `C`.

 |7|6-0|
 |:-:|:-:|
 |C|A\[6:0\]|

 It's usually used to **set** PSW's **CY** flag. It's work for instruction that only affected CY flag(SETB C, DA A, CPL C, etc..)
 
### 13. SETOVCLRCY
Set `A[7]` to 0, and set `A[2]` to `C`. 
|7|6-0|
|:-:|:-:|
|C|A\[6:0\]|

It's usually used to **set OV** flag and **cl**ea**r** **CY** flag. It's work for instruction MUL AB and DIV AB.

### 14. CHIRQ
Of all the bits that are 1, set the highest one to 0. 

|7-0|
|:-:|
|CHIRQ|

It's used to **C**lear **H**ighest **IRQ** in ISR when IRET instruction executed.


### 15. SWAP
**Swap** the nibble within the `A`.

|7-4|3-0|
|:-:|:-:|
|A\[3:0\]|A\[7:4\]|


# ALUD
## input and output
ALUD is a double operands ALU, it have four part inputs, two 4-bit operand `A``B`,  and a function select input `S`, a 1-bit operand `C`.
It have two  4-bit ouput `LQ` and `HQ`.

```python
     ┏━━━━━━━━━━┓
   ┌ ┫A0        ┃
   │ ┫.         ┃
 A ┥ ┫.       D0┣ ┐
   └ ┫.   A    .┣ │
   ┌ ┫.   T    .┣ ├ LQ
   │ ┫.   2    .┣ ┘
 B ┥ ┫.   8    .┣ ┐
   └ ┫.   C    .┣ │
   ┌ ┫.   6    .┣ ├ HQ
   │ ┫.   4   D7┣ ┘
 S ┥ ┫.         ┃
   └ ┫.         ┃
 C ─ ┫A12       ┃
     ┗━━━━━━━━━━┛
```

Obviously,only one chip can't perform two 8-bit input one 8-bit output function, but we can combine two chip togther. For function like `AND` `OR`, they don't need info from low part, lower nibble and high nibble can calculate indvidually and combine the output to one 8-bit output. For one chip, one function only using 4-bit ouput, and we can using another 4-bit for another function, for example, we can encode `AND` and `OR` in one S input:

```python
     ┏━━━━━━━━━━┓
   A ┫   AT28   ┃
   B ┫   C64    ┣ LQ: A or B
   S ┫          ┣ HQ: A and B
   C ┫          ┃
     ┗━━━━━━━━━━┛
```

But form function like `ADD`, `SUB`, the need carry signal from low part, we need some ouput to perform carry out ouput. In my design, HQ was used as carry out ouput(although carry out need only 1 bit), so one `S` can only encode one function for these case:
```python
      ┏━━━━━━━━━━┓
    ┌ ┫A0        ┃
    │ ┫.         ┃
 AL ┥ ┫.       D0┣ ┐
    └ ┫.   A    .┣ │
    ┌ ┫.   T    .┣ ├ AL + BL
    │ ┫.   2    .┣ ┘
 BL ┥ ┫.   8    .┣ 
    └ ┫.   C    .┣ 
    ┌ ┫.   6    .┣        CY
    │ ┫.   4   D7┣ ───────┴─────┐
  S ┥ ┫.         ┃              │
    └ ┫.         ┃              │
  C ─ ┫A12       ┃              │
      ┗━━━━━━━━━━┛              │
                                │
      ┏━━━━━━━━━━┓              │
    ┌ ┫A0        ┃              │
    │ ┫.         ┃              │
 AH ┥ ┫.       D0┣ ┐            │
    └ ┫.   A    .┣ │            │
    ┌ ┫.   T    .┣ ├ AH + BH    │
    │ ┫.   2    .┣ ┘            │
 BH ┥ ┫.   8    .┣              │
    └ ┫.   C    .┣              │
    ┌ ┫.   6    .┣              │
    │ ┫.   4   D7┣ ─ CY         │
  S ┥ ┫.         ┃              │
    └ ┫.         ┃              │
  C┌─ ┫A12       ┃              │
   │  ┗━━━━━━━━━━┛              │
   └────────────────────────────┘
```

<!-- ## encoding
The number in first column are the upper nibble, the number in fisrt row  are the lower nibble.

|name|0|1|2|3|
|:-:|:-:|:-:|:-:|:-:|
|0|A|NA|CAA|SFR|
|1|RR|RL|RRC|RLC|
|2|INC|DEC|BADDR|BIDX|
|3|SETCY|SETOVCLRCY|CHIRQ|SWAP|

## Description -->
