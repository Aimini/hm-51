import optparse
import os
import sys
import tokenize
import json
import enum


class cstate(enum.Enum):
    ERROR = enum.auto()
    START = enum.auto()
    NAME = enum.auto()  # you get a name, but, is it a parameterized control labal, or jump label, or...
    CONTROL_LINEEND = enum.auto()  # it's a control label, and now it's in end of the line
    CONTROL = enum.auto()   # control label too, not at end of the line
    JUMP_MARK = enum.auto()  # jump name
    PARAMETER_LIST_BEGIN = enum.auto()  # check wheather a parameter at next token
    NEXT_NAME = enum.auto()  # name after parameterized control name list
    CONVERT = enum.auto()  # you accumulated all the control names in this line, you should convert it to control signal now

    # sub state of PARAMETER_LIST_BEGIN
    PAR_SEPERATE = enum.auto()
    GET_ONE_PARAMETER = enum.auto()
    PARAMETER_LIST_END = enum.auto()


    def next(self, token):
        """
        according current state and t transfer to next state.
        see transfer diagram at directory
        state:
            current state
        t:
            token
        """
        ttype = token.type
        tstr = token.string
        if ttype in (tokenize.COMMENT, tokenize.ENCODING):
            if not self.isnoconsume():
                return self
        is_name = ttype == tokenize.NAME
        is_number = ttype == tokenize.NUMBER
        is_lineend = ttype in (tokenize.ENDMARKER, tokenize.NEWLINE) or ttype == tokenize.NL
        is_op = ttype == tokenize.OP

        
        scls = type(self)
        def check_op(s): return is_op and tstr == s

        if self == scls.START:
            if is_name:
                return scls.NAME
            if is_lineend:
                return scls.START
            else:
                return scls.ERROR
        elif self == scls.NAME:
            if is_op:
                if tstr == ',':
                    return scls.CONTROL
                elif tstr == ':':
                    return scls.JUMP_MARK
                elif tstr == '(':
                    return scls.PARAMETER_LIST_BEGIN
                else:
                    return scls.ERROR
            elif is_lineend:
                return scls.CONTROL_LINEEND
            else:
                return scls.ERROR
        elif self == scls.CONTROL_LINEEND:
            return scls.CONVERT
        elif self == scls.CONTROL:
            if is_name:
                return scls.NAME
            else:
                return scls.ERROR
        elif self == scls.JUMP_MARK:
            if is_name:
                return scls.NAME
            elif is_lineend:
                return scls.START
            else:
                return scls.ERROR
        elif self == scls.PARAMETER_LIST_BEGIN:
            if is_name or is_number:
                return scls.GET_ONE_PARAMETER
            elif check_op(')'):
                return scls.PARAMETER_LIST_END
        elif self == scls.NEXT_NAME:
            if is_name:
                return scls.NAME
            else:
                return scls.ERROR
        elif self == scls.CONVERT:
            return scls.START

        ####### sub state of S6
        elif self == scls.PAR_SEPERATE:
            if check_op(')'):
                return scls.PARAMETER_LIST_END
            elif is_name or is_number:
                return scls.GET_ONE_PARAMETER
            else:
                return scls.ERROR
        elif self == scls.GET_ONE_PARAMETER:
            if check_op(','):
                return scls.PAR_SEPERATE
            elif check_op(')'):
                return scls.PARAMETER_LIST_END
            else:
                return scls.ERROR
        elif self == scls.PARAMETER_LIST_END:
            if is_lineend:
                return scls.CONVERT
            elif check_op(','):
                return scls.NEXT_NAME
            else:
                return scls.ERROR
        else:
            return scls.ERROR

    def isnoconsume(self):
        scls = type(self)
        return self in (scls.CONVERT, scls.CONTROL_LINEEND)

    def iserror(self):
        pass


class statement_accumulator:
    """
    control accumulator pack tokens to a control label
    parameterized control label or jump label.
    """

    def __init__(self):
        self.parameters_owner = None
        self.parameters = []

        self.mark_lines = []
        self.marks_per_line = []
        pass

    def add(self, state, appendtokens):
        if state in (cstate.CONTROL_LINEEND, cstate.CONTROL):
            self.marks_per_line.append(appendtokens[-2])
        elif state == cstate.PARAMETER_LIST_BEGIN:
            self.parameters_owner = appendtokens[-2]
        elif state == cstate.GET_ONE_PARAMETER:
            self.parameters.append(appendtokens[-1])
        elif state == cstate.PARAMETER_LIST_END:
            self.marks_per_line.append([self.parameters_owner, self.parameters])
            self.parameters = []
        elif state == cstate.CONVERT:
            self.mark_lines.append(self.marks_per_line)
            self.marks_per_line = []
        

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

    state = cstate.START
    previous_state = state  # debug
    sa = statement_accumulator()
    for t in tks:

        previous_state = state
        while True:
            state = state.next(t)        
            scanned_tokens.append(t)
            if t.type == tokenize.NL or t.type == tokenize.NEWLINE:
                tokens_lines.append([])
            else:
                tokens_lines[-1].append(t)

            sa.add(state, scanned_tokens)
            if state == cstate.ERROR:
                estr = json.dumps(t.string).strip('"')
                e = SyntaxError()
                e.msg = "unexpect token \"{}\"".format(estr)
                e.lineno = t.start[0]
                e.offset = t.start[1]
                e.text = t.line
                e.filename = ""
                raise e
            # it does not consume any token
            elif state.isnoconsume():
                continue
            else:
                break

    for i in sa.mark_lines:
        for x in i:
            if isinstance(x, list):
                print(x[0].string,end = '')
                print("(", end = '')
                for y in x[1]:
                    print(y.string, end=',')
                print(")", end = '')
            else:
                print(x.string,end = '')
            print('',end = ',')
        print()

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
