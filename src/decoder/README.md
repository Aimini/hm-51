# Introduction
 One instruction consists of many micro instrcutions(MI), and an instruction execute only
 one MI in each clock cycle, each microinstruction cantain multiple micro-operations(MO) 
 to control hardwares. In our script syntax, each line is a MI,  and the mark like `RF(A,WE)` 
 will be translated to one or more MOs, compile will arrange MI's address and encode
 micro-opeartions according the LUTs.

# instruction execute flow
 An instruction execution flow can be divided into the following four stages:
 1. fetch
 2. decode
 3. execute
 4. check interrupt
 
 let's see what should we do in each stage.

## Fetch
- according `A`'s value set parity flag(PF) is `PSW`
- fetch instruction opcode from `ROM` to `IR`
- increase `PC`

## Decode
 it is essentially a big jump branch.Just like binary search, it's according `IR`'s value jump to corresponding address(we using jump mark in script).

## Execute
 That is the most important part, and we should do appropriate things to make the behavior of the instruction consistent with that described in the instruction set manual.

## Check interrupt
According `IRQ`, register `ISR`  `IE` `IP` to select highest priority `IRQ` and append it to `ISR`, then set `PC` to interrupt vector address.

# Conventions
For shrink some instruction cycle, The decoder script is follow the following conventions:
 - Stage fetch, leavel `PC+1` in `WR` and `SR` after increase `PC`. So that, for some instruction need to load data after opcode, we don't need to load `PC` from `RF` to `WR` and `SR` again.