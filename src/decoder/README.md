# Decoder Script Document  <!-- omit in toc -->
---
# Table of Content  <!-- omit in toc -->
- [Introduction](#introduction)
- [Instruction Execute Flow](#instruction-execute-flow)
  - [fetch](#fetch)
  - [decode](#decode)
  - [execute](#execute)
  - [check interrupt](#check-interrupt)
- [Stage Reset All](#stage-reset-all)
- [Conventions](#conventions)

## Introduction

 One instruction consists of many micro instrcutions(MI), and an instruction execute only one MI in each clock cycle, each microinstruction cantain multiple micro-operations(MO) to control hardwares.

 In our script syntax, each line is a MI, and the mark like `RF(A,WE)` will be translated to one or more MOs, compiler will arrange MI's address and encode micro-opeartions according to the LUTs.

## Instruction Execute Flow

 An instruction execution flow can be divided into the following four stages:

 1. fetch
 2. decode
 3. execute
 4. check interrupt

 Let's see what should we do in each stage.

### fetch
* load PC to WR,SR
* set parity flag(PF) in `PSW` according to `A`'s value .
* fetch instruction opcode from `ROM` to `IR`.
  
I put increasing `PC` to decode stage.
### decode

it is essentially like a interrupt vector, when decode a opcode, I use `(IR << 1) + 1` to generate first microinstruction's address of each instruction. Obviously a vector only can support 2 microinstruction so I put execution stage in other places and jump to there in decode vector. It happens to that increasing PC stage only need 2 microinstruction, so I put increasing `PC` in decode stage.

  increase `PC`.
### execute

 That is the most important part, and we should do appropriate things to make the behavior of the instruction consistent with that described in the instruction set manual.

### check interrupt

According `IRQ` , register `ISR`  `IE`  `IP` to select highest priority `IRQ` and append it to `ISR` , then set `PC` to interrupt vector address.

## Stage Reset All

 Considering that some register file chips do not have a reset input (maybe you are using a dual-port RAM chip as a register file chip), we can't reset the contents of the register through the hardware-level reset pin.

 Therefore, I added a piece of MI code for resetting the register contents (including PC). When the RESET input is high, MIPC will jump to this code and return to the FETCH stage after execution.

## Conventions

 For shrink some instruction cycle, The decoder script is follow the following conventions:

 *Stage decode*
- leavel `PC+1` in `WR` and `SR` after increase `PC` . So that, for some instruction need to load data that after opcode, we don't need to load `PC` from `RF` to `WR` and `SR` again.

- leavel 0 in `BR` for instruction that need using 0 or 1 in `BR`.

 *Stage reset*
- set `T3` to 0 and never modify it.