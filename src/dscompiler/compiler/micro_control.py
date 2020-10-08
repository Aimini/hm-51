CONTROL = "CONTROL"
JUMP_MARK = "JUMP_MARK"
PAR_CONTROL = "PAR_CONTROL"


class MicroCTL():
    def __init__(self, lineno, t, v):
        self.lineno = lineno
        self.type = t
        self.value = v
        self.parameters = []

    def simple_str(self):
        s = self.value

        if self.type == PAR_CONTROL:
            s += '('
            sp = []
            for _ in self.parameters:
                if isinstance(_, int):
                    sp.append("0x{:X}".format(_))
                else:
                    sp.append(_)
            s += ','.join(sp)
            s += ')'
        elif self.type == JUMP_MARK:
            s += ':'
        return s

    def __str__(self):
        s = self.type + ':' + self.simple_str()
        if self.type == JUMP_MARK:
            s = s[0:-1]

        return s

    def __repr__(self):
        return self.__str__()

    def copy(self):
        ret = MicroCTL(self.lineno,self.type,self.value)
        ret.parameters = self.parameters
        return ret