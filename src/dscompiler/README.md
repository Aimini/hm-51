# Decoder Script Compiler Document
---
## Script Syntax

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