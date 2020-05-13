import optparse
import os
import sys
import io
import tokenize
import pathlib
import codecs

import dtoken_converter
import hl_dtoken_converter
import dtoken_compiler


def dissassemble(write, bytes_len, source_lines, machine_code_lines, hl_dtoken_lines):
    mcidx = 0
    hlidx = 0
    for idx, t in enumerate(source_lines):
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
                write(', '.join([_.simple_str() for _ in hl_dtoken_lines[hlidx][1]]))
                hlidx += 1
                write('\n')


def preprocess_args(args_str):
    """
    convert string like  '"s0","a+b","c+d"' to a list like ['s0', 'a+b', 'c+d']
        args_str: str

    """
    ARG_END = 'ARG_END'
    ARG_BEGIN = 'ARG_BEGIN'
    ARG_SPLIT = 'ARG_SPLIT'
    state = ARG_SPLIT

    arg_list = []
    start_idx = 0
    for current_idx, c in enumerate(args_str):
        if c.isspace():
            continue

        if state == ARG_END:
            if c == ',':
                state = ARG_SPLIT
            else:
                pass
                e = SyntaxError('unexcept double quates')
                e.offset = current_idx
                raise e
        elif state == ARG_BEGIN:
            if c == '"':
                state = ARG_END
                arg_list.append(args_str[start_idx:current_idx])
        elif state == ARG_SPLIT:
            if c == '"':
               state = ARG_BEGIN
               start_idx = current_idx + 1
            else:
                e = SyntaxError('unexcept char \'{}\''.format(c))
                e.offset = current_idx
                raise e

    if state is ARG_BEGIN:
        e = SyntaxError('unclosed string literal "{}"'.format(args_str[start_idx - 1]))
        e.offset = start_idx - 1
        raise e
    return arg_list


def preprocess_include(line, filename):
    ret_str = ""
    args = preprocess_args(line.strip()[4:].strip())
    include_filename_str = str(pathlib.Path(filename).parent / args[0])

    ret_str += '\n#>>>>>>>>>>>>>> include file "{}" start. >>>>>>>>>>>>'.format(include_filename_str)
    ret_str += '\n#>>> {}\n'.format(line)
    with open(include_filename_str) as inc_fh:
        content = inc_fh.read()
        for idx, one_arg in enumerate(args[1:]):
            content = content.replace(f"@{idx}", one_arg)
        ret_str += content
    ret_str += '\n#<<<<<<<<<<<<<<<<<<< "{}" end. <<<<<<<<<<<<<<<<<<<<<<\n'.format(include_filename_str)
    return ret_str


def preprocess(filename):
    file_need_preprocess = io.StringIO(open(filename).read())
    need_preprocess = True

    while need_preprocess:
        need_preprocess = False
        file_need_preprocess.seek(0)
        file_preprocessed = io.StringIO()

        for line in file_need_preprocess.readlines():
            pt = line.strip().split()

            #include process, @INC "filename", "arg0", "arg1"
            if len(pt) < 1 or pt[0] != '@INC':
                file_preprocessed.write(line)
            else:
                need_preprocess = True
                file_preprocessed.write(preprocess_include(line, filename))

        file_need_preprocess = file_preprocessed

    file_need_preprocess.seek(0)
    return file_need_preprocess


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
    hlc = hl_dtoken_converter.hl_dtoken_converter()
    c = dtoken_compiler.dtoken_compiler()
    c.calcuate_LUT_parameters_position()

    controls_parameters_position_info = c.controls_parameters_position_info()

    bits_len = 0  # have many bits using to encoding
    pos_fmt_str = "{:>8} {:>8} {:>16}"
    print(pos_fmt_str.format("pos", "size", "name"))
    for pos, size, name in controls_parameters_position_info:
            bits_len = max(bits_len, pos + size)
            print(pos_fmt_str.format(pos, size, name))
    bytes_len = int((bits_len + 7)/8)  # how many bytes using to encoding, math.ceil(bits_len/8)

    dtoken_lines, pytoken_lines = dc.convert(tokenize.tokenize(readline))
    hl_token_lines = hlc.convert(dtoken_lines)
    machine_code_lines, pure_control_tokens_line = c.compile(hl_token_lines)

    [write(_[1].to_bytes(bytes_len, "little")) for _ in machine_code_lines]

    return bytes_len, pure_control_tokens_line, machine_code_lines


def compile_ds_to_file(fhi, outfile, dis_file):
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
        bytes_len, hl_token_lines, machine_code_lines = compile_ds(fhi.readline, fho.write)
        if dis_file is not None:
            fhi.seek(0)
            with open(dis_file, "w") as disfh:
                dissassemble(disfh.write, bytes_len, fhi.readlines(), machine_code_lines, hl_token_lines)

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
    preprocessed_file_obj = preprocess(infile)
    content = preprocessed_file_obj.read()
    if op.preprocess_file != None:
        with open(op.preprocess_file, "w") as fh:
            fh.write(content)
    try:
        outfile = op.output
        dis_file = op.dis_file

        if outfile == None:
            outfile = os.path.splitext(infile)[0] + '.bin'
        bl, l = compile_ds_to_file(io.BytesIO(content.encode('utf-8')), outfile, dis_file)
        kb = (bl * l)/1024
        print("line bytes:", bl)
        print("lines:", l)
        print("size:", kb, "KB")
    except SyntaxError as e:
        e.filename = infile
        raise e
