# Decoder Script Compiler Document
---
## Script Syntax
 The script describes the hardware control signals corresponding to each MIPC(microinstruction program counter), each line contains a set of component control tokens to describe what this component should do during this cycle.

### component control token

 As we mentioned before, component control tokens describes what the component should do. 
 
 The token are start by component name, the controls of this component are written in curly braces, multiple controls are separated by commas.

  A comopent control token are looks like this:
 ```python
 RF(A,WE)
 ```
  The `RF` is the name of component `register file`, the `A` is meaning set `A`'s encoding to pin register selection, the `WE` meaing set `WE` enconding to write enable port.
  
  Multiple tokens at one line are separated by commas:
   ```python
  # increase A by 1
  RF(A,WE), ALU(INC), BR(CY)
 ```

  *named controls*

  The arguments of most tokens have name and this mechanism make these controls position-independent, which means that there is no difference between `RF(A,WE)` and `RF(WE,A)` under current LUT.
  
 For `RF`, because we are configured to use the name of the control to find its corresponding pin and encoding, compiler will try to resolve the name of these names and finally knows that `A` is the encoding of register selection pin, and `WE` is the encoding of write enable pin.

  *value controls*

  These types controls are used in components that contain immediate number, we can't assign a meaningful names to these numbers, they are just numbers:
  ```python
  # load immed value 0x80 to A
  RF(A,WE), IMMED(0x80), BUS(IMMED)
  ```

### composite-control token

### jump label

### macro


## Disassemble

## Change LUT

## More detail

Wanna to add new macros or add more abstract tokens?

Let's go.

### add composite-control translator

 Open file `/src/dscompiler/hl_dtoken_converter.py`, there, you can see a useless(abstract) class named `empty_translator`, you should write a class that inherits from it.

 It provides some memember functions for creating hardware level dtokens. You should pay attention to the following three functions:

  - prepare(): invoke it before scanning each line of dtokens.
  - scan(dtoken): invoke it for each dtoken in the line, use to get infomation from this line.
  - translate(dtoken): invoke it again for each dtoken in the line, use to return new dtoken.
  
 You can view more details in the comment of the class `empty_translator`, there are also some examples for reference: `alu_translator`,`load_immed_translator`, etc.

<!-- ### add new marco -->