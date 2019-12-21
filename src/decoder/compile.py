import optparse
import os
import sys
import tokenize
import json



def next_state(state, t):
    """
    according current state and t transfer to next state.
    see transfer diagram at directory
    state:
        current state
    t:
        token
    """
    ttype = t.type
    tstr = t.string

    def is_name():
        return ttype == tokenize.NAME

    is_name = ttype == tokenize.NAME
    is_number = ttype == tokenize.NUMBER
    is_newline = ttype == tokenize.NEWLINE or ttype == tokenize.NL
    is_op = ttype == tokenize.OP
    def check_op(s): return is_op and tstr == s

    if t.type in (tokenize.COMMENT, tokenize.ENCODING) and state not in (3, 10):
        return state

    elif state == 1:
        if is_name:
            return 2
        if is_newline:
            return 1
        else:
            return 0
    elif state == 2:
        if is_op:
            if tstr == ',':
                return 4
            elif tstr == ':':
                return 5
            elif tstr == '(':
                return 6
            else:
                return 0
        elif is_newline:
            return 3
        else:
            return 0
    elif state == 3:
        return 10
    elif state == 4:
        if is_name:
            return 2
        else:
            return 0
    elif state == 5:
        if is_name:
            return 2
        elif is_newline:
            return 1
        else:
            return 0
    elif state == 6:
        if is_name or is_number:
            return 6001
        elif check_op(')'):
            return 6002
    elif state == 10:
        return 1
    ####### sub state of S6
    elif state == 6001:
        if check_op(','):
            return 6
        elif check_op(')'):
            return 6002
        else:
            return 0
    elif state == 6002:
        if is_newline:
            return 10
        elif check_op(','):
            return 1
        else:
            return 0
    else:
        return 0


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
    tks = tokenize.tokenize(readline)
    # each line's tokens list
    tokens_lines = [[]]
    scanned_tokens = []
    state = 1
    previous_state = 1  # debug
    for t in tks:
        if t.type == tokenize.ENDMARKER:
            break

        previous_state = state
        state = next_state(state, t)
        while True:
            if state == 0:
                estr = json.dumps(t.string).strip('"')
                e = SyntaxError()
                e.msg = "unexpect token \"{}\"".format(estr)
                e.lineno = t.start[0]
                e.offset = t.start[1]
                e.text = t.line
                e.filename = ""
                raise e
            # it does not consume any token
            elif state in (10, 3):
                state = next_state(state, t)
            else:
                break

        scanned_tokens.append(t)
        if t.type == tokenize.NL or t.type == tokenize.NEWLINE:
            tokens_lines.append([])
        else:
            tokens_lines[-1].append(t)


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
    darg = ['-i', R"D:\OneDrive\51cpu\src\decoder\decoder.ds"]
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
