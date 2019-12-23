import optparse
import os
import sys
import tokenize
import dtoken_converter
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
    """
    sa = dtoken_converter.dtoken_converter()
    dtoken_lines,pytoken_lines = sa.convert(tokenize.tokenize(readline))
    c = dtoken_compiler.dtoken_compiler(13)
    c.compile(dtoken_lines)
    

def compile_ds_to_file(infile, outfile):
    """
    parameters
        infile :
            input filename.
        outfile :
            ouput filename.
    """
    fhi = open(infile, "rb")
    fho = open(outfile, "wb")
    compile_ds(fhi.readline, fho.write)


if __name__ == "__main__":
    arg_parser = optparse.OptionParser()
    arg_parser.add_option('-i', '--input', action='store', type="string", dest='input')
    arg_parser.add_option('-o', '--output', action='store', type="string", dest='output', default=None)

    # iarg = sys.argv[1:]
    darg = ['-i', R"D:\OneDrive\51cpu\src\decoder\test.ds"]
    iarg = darg

    op, ar = arg_parser.parse_args(darg)
    infile = op.input
    outfile = op.output
    if outfile == None:
        outfile = os.path.splitext(infile)[0] + '.bin'
    try:
        compile_ds_to_file(infile, outfile)
    except SyntaxError as e:
        e.filename = infile
        raise e
