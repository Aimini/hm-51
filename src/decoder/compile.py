import optparse
import os
import sys
import io
import tokenize

import dtoken_converter
import hl_dtoken_converter
import dtoken_compiler

def dissassemble(write,bytes_len,source_lines, machine_code_lines, hl_dtoken_lines):
    mcidx = 0
    hlidx = 0
    for idx,t in enumerate(source_lines):
        x = idx + 1
        write('{:>5d}: '.format(x))
        write(t.decode('utf-8').strip())
        write('\n')

        if mcidx < len(machine_code_lines):
            if x == machine_code_lines[mcidx][0]:
                write('[{:0>4X}]'.format(mcidx))
                write(('{:0>' + str(bytes_len*2) + 'X} ').format(machine_code_lines[mcidx][1]))
                mcidx += 1


        if hlidx < len(hl_dtoken_lines):
            if x == hl_dtoken_lines[hlidx][0]:
                write(', '.join([ _.simple_str() for _ in hl_dtoken_lines[hlidx][1]]))
                hlidx += 1
                write('\n')

        # write(','.join([ _.simple_str() for _ in hl_dtokens_per_line[1]]))
        # write('\n')
        # lineno += 1


def compile_ds(readline, write):
    """
    parameters
        readline :
            must be a callable object which provides the same interface as the io.IOBase.readline() method of file objects.
            readline return a bytes array, the function will auto detect encode.

        write :
            must be a callable object which provides the same interface as the io.RawIOBase.write() method of file objects.
            namely, write(bytes) can write a bytes stream to traget. 
        
        return:tuple(int, list, list)
            ret[0] is bytes per line
            ret[1] is a pure control dtoken object list
            [
                [lineno, [dtoken,dtoken,...]],
                [lineno, [dtoken,dtoken,...]],
                ...
            ]
            ret[2] is a list contain lineno and machine_code
            [
                [lineno, machine_code],
                [lineno, machine_code],
                ...
            ]

    """


    dc = dtoken_converter.dtoken_converter()
    hlc =  hl_dtoken_converter.hl_dtoken_converter()
    c = dtoken_compiler.dtoken_compiler()
    c.calcuate_LUT_parameters_position()

    controls_parameters_position_info = c.controls_parameters_position_info()
    
    bits_len = 0 # have many bits using to encoding
    pos_fmt_str = "{:>8} {:>8} {:>16}"
    print(pos_fmt_str.format("pos","size","name"))
    for pos,size,name in controls_parameters_position_info:
            bits_len = max(bits_len,pos + size)
            print(pos_fmt_str.format(pos,size,name))
    bytes_len = int((bits_len + 7)/8) # how many bytes using to encoding, math.ceil(bits_len/8)
    
    dtoken_lines,pytoken_lines = dc.convert(tokenize.tokenize(readline))
    hl_token_lines = hlc.convert(dtoken_lines)
    machine_code_lines,pure_control_tokens_line = c.compile(hl_token_lines)
    
    [write(_[1].to_bytes(bytes_len, "little")) for _ in machine_code_lines]

    return bytes_len, pure_control_tokens_line, machine_code_lines

def compile_ds_to_file(infile, outfile, dis_file):
    """
    parameters
        infile :
            input filename.
        outfile :
            ouput filename.
                
        return:tuple(int, int)
            t[0] is bytes per line
            t[1] is how many lines
    """
    with open(infile, "rb") as fhi, open(outfile, "wb") as fho:
        bytes_len, hl_token_lines, machine_code_lines = compile_ds(fhi.readline, fho.write)
        if dis_file is not None:
            fhi.seek(0)
            with open(dis_file,"w") as disfh:
                dissassemble(disfh.write, bytes_len, fhi.readlines() ,machine_code_lines, hl_token_lines)
        
        
        return bytes_len, len(machine_code_lines)

if __name__ == "__main__":
    arg_parser = optparse.OptionParser()
    arg_parser.add_option('-i', '--input', action='store', type="string", dest='input')
    arg_parser.add_option('-o', '--output', action='store', type="string", dest='output', default=None)
    arg_parser.add_option('-d', '--dissassemble-file', action='store', type="string", dest='dis_file', default=None)

    iarg = sys.argv[1:]
    darg = ['-i', R"C:\Users\abb\OneDrive\51cpu\src\decoder\decoder.ds","-d", R"decoder.disa"]

    op, ar = arg_parser.parse_args(iarg)
    infile = op.input
    outfile = op.output
    dis_file = op.dis_file
    if outfile == None:
        outfile = os.path.splitext(infile)[0] + '.bin'
    try:
        bl,l = compile_ds_to_file(infile, outfile, dis_file)
        kb = (bl * l)/1024
        print("line bytes:",bl)
        print("lines:",l)
        print("size:",kb,"KB")
    except SyntaxError as e:
        e.filename = infile
        raise e
