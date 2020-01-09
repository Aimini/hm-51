# introduction

# manual test instructions
We first implement the following two instructions:
   - MOV direct, #immed
   - MOV direct, direct

 Why? using first instruction we can move any immediate number to any 
 address(include all SFR in RF). Using the second instruction, we can move
 any data from one memory cell/register to another memory cell/register.
 When we implement these two isntructions and make sure they work properly,
 then we can using  hardware assertion to check other instrcutions' result.
 (memory cell equal to immediate, ne register equal to another register etc).
