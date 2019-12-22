##########################################
# 2019-12-22 12:44:23
# AI
# dtoken compiler, compile all dtoken in all lines to 
# machine code
##########################################
import enum
import tokenize
import dtoken
import json

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
                return scls.CONVERT
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


class dtoken_converter:
    """
    control accumulator pack tokens to a control label,
    parameterized control label or jump label.
    result store in memeber list self.dtoken_lines
    dtoken_lines[n][0] is line number in source file
    dtoken_lines[n][1] is a list of decoders' tokens at this line
    """

    def __init__(self):
        self.parameters_owner = None
        self.parameters = [] #store control's parameters

        self.dtoken_lines = [] 
        self.marks_per_line = [] # all marks in one(current) line


    def dtoken_from_pytoken(self, pytoken, dtype):
        # line, type, name
        return dtoken.dtoken(pytoken.start[0], dtype, pytoken.string)
        
    def add(self, state, appendtokens):
        """
            according state and appendtokens to generate decoder token

        """
        t1 = appendtokens[-1]
        #find control mark
        if state in (cstate.CONTROL_LINEEND, cstate.CONTROL):
            # name, ','
            # name, '\n\r'
            dt2 = self.dtoken_from_pytoken(appendtokens[-2],None)
            dt2.type = dtoken.CONTROL
            self.marks_per_line.append(dt2)
        #find jump mark
        elif state == cstate.JUMP_MARK:
            # name , ':'
            dt2 = self.dtoken_from_pytoken(appendtokens[-2],None)
            dt2.type = dtoken.JUMP_MARK
            self.marks_per_line.append(dt2)
        elif state == cstate.PARAMETER_LIST_BEGIN:
            # name , "("
            self.parameters_owner = appendtokens[-2]
        elif state == cstate.GET_ONE_PARAMETER:
            if t1.type == tokenize.NUMBER:
                self.parameters.append(int(t1.string,0))
            else:
                self.parameters.append(t1.string)
        elif state == cstate.PARAMETER_LIST_END:
            t = self.dtoken_from_pytoken(self.parameters_owner, dtoken.PAR_CONTROL)
            t.parameters = self.parameters
            self.marks_per_line.append(t)
            self.parameters = []
        elif state == cstate.CONVERT:
            self.dtoken_lines.append([self.marks_per_line[0].lineno, self.marks_per_line])
            self.marks_per_line = []

    def convert(self,pytokens_iter):
        pytoken_lines = [[]]
        scanned_tokens = []
        # clear
        self.dtoken_lines = []
        self.parameters = []
        self.marks_per_line = []

        state = cstate.START
        previous_state = state  # debug

        for t in pytokens_iter:
            previous_state = state
            scanned_tokens.append(t)
            if t.type == tokenize.NL or t.type == tokenize.NEWLINE:
                pytoken_lines.append([])
            else:
                pytoken_lines[-1].append(t)

            while True:
                # don't care
                if t.type == tokenize.COMMENT or t.type == tokenize.ENCODING:
                    break

                state = state.next(t)
                self.add(state, scanned_tokens)
                if state == cstate.ERROR:
                    estr = json.dumps(t.string).strip('"')
                    e = SyntaxError()
                    e.msg = 'unexpect token "{}"'.format(estr)
                    e.lineno = t.start[0]
                    e.offset = t.start[1]
                    e.text = t.line
                    e.filename = ''
                    raise e
                # it does not consume any token
                elif state.isnoconsume():
                    continue
                else:
                    break
                
        return self.dtoken_lines, pytoken_lines