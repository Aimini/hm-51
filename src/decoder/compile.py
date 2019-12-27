import optparse
import os
import sys
import tokenize
import dtoken_converter
import hl_dtoken_converter
import dtoken_compiler
def compile_ds(readline, write):
    """
    parameters
        readline :
            must be a callable object which provides the same interface as the io.IOBase.readline() method of file objects.
            readline return a bytes array, the function will auto detect encode.
        write :
            must be a callable object which provides the same interface as the io.RawIOBase.write() method of file objects.
            namely, write(bytes) can write a bytes stream to traget. 
        
        return:tuple(int, int)
            t[0] is bytes per line
            t[1] is how many lines

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
    machine_code_lines = c.compile(hl_token_lines)
    [write(_.to_bytes(bytes_len, "little")) for _ in machine_code_lines]

    return bytes_len, len(machine_code_lines)

def compile_ds_to_file(infile, outfile):
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
        return compile_ds(fhi.readline, fho.write)


if __name__ == "__main__":
    arg_parser = optparse.OptionParser()
    arg_parser.add_option('-i', '--input', action='store', type="string", dest='input')
    arg_parser.add_option('-o', '--output', action='store', type="string", dest='output', default=None)

    iarg = sys.argv[1:]
    darg = ['-i', R"decoder.ds"]

    op, ar = arg_parser.parse_args(iarg)
    infile = op.input
    outfile = op.output
    if outfile == None:
        outfile = os.path.splitext(infile)[0] + '.bin'
    try:
        bl,l = compile_ds_to_file(infile, outfile)
        kb = (bl * l)/1024
        print("line bytes:",bl)
        print("lines:",l)
        print("size:",kb,"KB")
    except SyntaxError as e:
        e.filename = infile
        raise e
