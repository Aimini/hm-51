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
 Composite-control tokens are looks like normal tokens, but it perform an higher level of abstraction(provides a simpler way of writing). A composite-control tokens can be translated into one or more component control tokens.
 
 For example,  `LI(0x80)` means that you want to using the immediate value 0x80 to drive the bus. Obviously, you want the `IMMED` component to drive the bus, so it's best to convert it to `BUS(IMMED), IMMED(0x80)`.

 See [this](###-add-composite-control-translator) for how to add customer composite-control token.


### jump label
 When you need to get the MIPC value corresponding to a line of microinstructions (usually a jump token), using the jump label can let the compiler help you get these (not easy to manually calculate) values.

 The jump label starts with its name, followed by a colon:

 ```python
 SEG_HELLO:
```

 If the jump label is on a separate line, it represents the MIPC value of the microinstruction on the next line.

 If the jump label and the microinstruction are on the same line, it represents the MIPC value of the microinstruction in the current line.
 ```python
# jump if less than(A < 0x80)
RF(A), JTYPE(JLT), IMMED(0x80), ADDRESS(SEG_TEST)
# something A >= 0x80
# ...

#---- at different lines
SEG_TEST: # <- jump label
# something A < 0x80
# ...
JTYPE(JMP), ADDRESS(SEG_END)

#---- at same line
SEG_END: RF(A,WE), LI(0x80)
# ^
# jump label
```
The jump label is ensstianlly a number, it's the value of the MIPC corresponding to the line where the label is located, so the following example will work:

 ```python
 TEST_MIPC: 
 # TEST_MIPC represents a number, it's legal.
 IMMED(TEST_MIPC), BUS(IMMED)
 # 0xABC is a magic number, but it's legal too.
 JTYPE(JMP), ADDRESS(0xABC) 
 ```
 
 In the decoder script, you will use a large number of jump tokens to decode the opcode. Jump labels can provide meaningful name for code segments.



### directive
 The directive starts with '@', followed by the directive name. No space is allowed between '@' and the name, the space after the name separates the directive name and the arguments. The arguments are separated by commas, all arguments are string literals:

 ``` powershell
 #example
 @INC "test.ds","1","2"
 ^ ^  ^-------+-------^
 | |       arguments
 | name
 directive symbol
 ```
 *directive @INC*

  We only support one directive `@INC`, it's used to reuse code, this is the arguments meaning of `@ INC`:

  ``` powershell
  @INC "filename","ph0","ph1",...,"phN"
  ```
  Obviously, first argument is filename that will be included, "ph0" is placeholder 0, "ph1" is placeholder 1. 
  
  What is placeholder? It's a string that will be insert into included file, for eaxmple:

  ```powershell
  # file top.ds
  @INC "2.ds","0", "1"
  ```
  ```powershell
  #file 2.ds
  INC_ME(HEL)
  @0, @1
  INC_END(HEL)
  ```
  This is content after preprocess:
  ```powershell
  INC_ME(HEL)
  0, 1
  INC_END(HEL)
  ```
  
  Another example:

  ```powershell
  # file 1.ds
  IAM(TOP)
  @INC "2.ds","HELLO", "WORLD", ")"
  ```
  ```powershell
  #file 2.ds
  INC_ME(HEL)
  @0(@1 @2
  INC_END(HEL)
  ```
  After preprocess:
  ```powershell
  IAM(TOP)
  INC_ME(HEL)
  HELLO(WORLD)
  INC_END(HEL)
  ```

  In the current design, preprocessing will do these things:

   - copies the contents of the file in the @INC directive.
   - replace placeholder in the content.
   - paste it into the current file, replacing the line with `@INC`.


## Disassemble
 In the case you want to correct syntax errors or view the tokens of the composite-control is transalted, you can using the disassemble function of compile.py.

 ### view the preprocessed file
  The compiler's will show syntax error base on preprocessd text, Uinsg the `-s` argument will let compiler dump the preprocessed text to target file:

  ```python
  compile.py -s <preprocessed_file> -i <input_file> -o <ouput_file>
  ```

### view the machine code and MIPC
 Using `-d` can dump more information about you decoder script, it's provide more powerful tool to inspect the control token conflicts or hardware desgin issues.

 ```
 compile.py -d <disassemble_file> -i <input_file> -o <ouput_file>
 ```
 
 This is example of one microinstruction:
 ```
   17: RF(A),      ALU(PF),   BR(ALUDF)
[0003]000000102886 RF(A), ALUSD(PF), BUS(ALUDH), BR(ALUDF) 
```
The first line is the original text in preprocessed file, the second line  is addidtional information(hardware level) about the first line. 

Here is the meaning of each part:
```
   17: RF(A),      ALU(PF),   BR(ALUDF)
   ^   ^------------+----------------^
   |          original tokens     
line number
  
[0003]000000102886 RF(A), ALUSD(PF), BUS(ALUDH), BR(ALUDF) 
  ^       ^         ^-----------------+-----------------^
  |       |                 hardware level tokens
  |       |       (traslated from composite-control tokens)      
  |  machine code
 MIPC
```
## Change LUT
 The LUT is used to define the component and its control pins, include describe the name of the component, the function encoding and bit index of the control pins.

 Please refer to the comments in the file "/src/compiler/control_LUT.py" for more details.

## More detail

Wanna to add new directive or add composite-control tokens?

Let's go.

### add composite-control translator

 Open file `/src/dscompiler/hl_dtoken_converter.py`, there, you can see a useless(abstract) class named `empty_translator`, you should write a class that inherits from it.

 It provides some memember functions for creating hardware level dtokens. You should pay attention to the following three functions:

  - prepare(): invoke it before scanning each line of dtokens.
  - scan(dtoken): invoke it for each dtoken in the line, use to get infomation from this line.
  - translate(dtoken): invoke it again for each dtoken in the line, use to return new dtoken.
  
 You can view more details in the comment of the class `empty_translator`, there are also some examples for reference: `alu_translator`,`load_immed_translator`, etc.

<!-- ### add new marco -->