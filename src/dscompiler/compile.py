import optparse
import os
from os import sep
from shlex import quote
import sys
from compiler import preprocessor
from compiler import parser
from compiler.micro_control_converter.micro_control_converter import MicroControlConverter,DecvecConverter
from compiler.micro_instruction_compiler import MicroinstrcutionCompiler
from compiler.preprocessor import PreprocessError
from compiler.compile_error import CompileError


def dissassemble(write, bytes_len, source_lines, machine_code_lines, hl_dtoken_lines):
    mcidx = 0
    for idx, t in enumerate(source_lines):
        x = idx + 1
        write('{:>5d}: '.format(x))
        write(t.strip())
        write('\n')

        while mcidx < len(machine_code_lines) and x == machine_code_lines[mcidx][0]:
            write('[{:0>4X}]'.format(mcidx))
            write(('{:0>' + str(bytes_len*2) + 'X} ').format(machine_code_lines[mcidx][1]))
            write('\n')
            write(', '.join([_.simple_str() for _ in machine_code_lines[mcidx][2]]))
            write('\n')
            mcidx += 1

        # while hlidx < len(hl_dtoken_lines) and  x == hl_dtoken_lines[hlidx][0]:
        
        #     hlidx += 1
        #     write('\n')








def compile_ds(readline, write,veclineno, vecnum):
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

    c =     MicroinstrcutionCompiler()
    c.calcuate_LUT_parameters_position()

    controls_parameters_position_info = c.controls_parameters_position_info()

    bits_len = 0  # have many bits using to encoding
    pos_fmt_str = "{:>8} {:>8} {:>16}"
    print(pos_fmt_str.format("pos", "size", "name"))
    for pos, size, name in controls_parameters_position_info:
            bits_len = max(bits_len, pos + size)
            print(pos_fmt_str.format(pos, size, name))
    bytes_len = int((bits_len + 7)/8)  # how many bytes using to encoding, math.ceil(bits_len/8)

    dtoken_lines = parser.Parser().parse(readline)
    hl_token_lines = MicroControlConverter().convert(dtoken_lines)
    hl_token_lines = DecvecConverter(hl_token_lines, veclineno, vecnum ).result()
    
    machine_code_lines, pure_control_tokens_line = c.compile(hl_token_lines)

    [write(_[1].to_bytes(bytes_len, "little")) for _ in machine_code_lines]

    return bytes_len, pure_control_tokens_line, machine_code_lines


def compile_ds_to_file(fileobj,veclineno, vecnum, outfile, dis_file):
    """
    parameters
        infile :
            input file object, must be binary mode.
        outfile :
            ouput filename.
                
        return:tuple(int, int)
            t[0] is bytes per line
            t[1] is how many lines
    """

    with open(outfile, "wb") as fho:
        bytes_len, hl_token_lines, machine_code_lines = compile_ds(fileobj.readline, fho.write,veclineno, vecnum)
        if dis_file is not None:
            fileobj.seek(0)
            with open(dis_file, "w") as disfh:
                dissassemble(disfh.write, bytes_len, fileobj.readlines(), machine_code_lines, hl_token_lines)

        return bytes_len, len(machine_code_lines)


if __name__ == "__main__":
    arg_parser = optparse.OptionParser()
    arg_parser.add_option('-i', '--input', action='store', type="string", dest='input')
    arg_parser.add_option('-o', '--output', action='store', type="string", dest='output', default=None)
    arg_parser.add_option('-d', '--dissassemble-file', action='store', type="string", dest='dis_file', default=None)
    arg_parser.add_option('-s', '--preprocess-file', action='store', type="string",
                          dest='preprocess_file', default=None, help="the file to store preprocessed content.")
    iarg = sys.argv[1:]
    darg = ['-i', R"src\decoder\decoder.ds", "-o", R"temp\decoder.bin",
            "-d", R"temp\decoder.disa", '-s', R'temp\decoder.pre']

    op, ar = arg_parser.parse_args()

    infile = op.input
    outfile = op.output
    dis_file = op.dis_file
    
    pre = preprocessor.Preprocessor(infile)

    try:
        preprocessed_file = pre.result()
        if op.preprocess_file != None:
            with open(op.preprocess_file, "w") as fh:
                fh.write(preprocessed_file.read())
                preprocessed_file.seek(0)
                fh.close()

        if outfile == None:
            outfile = os.path.splitext(infile)[0] + '.bin'

        veclineno, vecnum = pre.decvecinfo()
        bl, l = compile_ds_to_file(preprocessed_file,veclineno, vecnum, outfile, dis_file)
        kb = (bl * l)/1024
        print("line bytes:", bl)
        print("lines:", l)
        print("size:", kb, "KB")
    except PreprocessError as e:
        for one in e.inc_chain_Info:
            print('File "{}", line {},'.format(str(one.file), one.row))
            if one.str[-1] in ('\n', '\r'):
                print("  ", one.str, end = '')
            else:
                print("  ", one.str)
        print('[preprocess error]', e.info, end= ' in @')
        print(e.directive, end = '(')
        print(', '.join("'" + _ + "'" for _ in e.args), end = ')')
    except CompileError as e:
        lineinfo = pre.getlineinfo(e.lineno)
        for one in lineinfo:
            print('File "{}", line {},'.format(str(one.file), one.row))
            if one.str[-1] in ('\n', '\r'):
                print("  ", one.str, end = '')
            else:
                print("  ", one.str)
        print(e.info)
         

        
        
