CONTROL = "CONTROL"
JUMP_MARK = "JUMP_MARK"
PAR_CONTROL = "PAR_CONTROL"

class dtoken():
    def __init__(self, lineno, t, v):
        self.lineno = lineno
        self.type = t
        self.value = v
        self.parameters = []

    def simple_str(self):
        s = self.value
        
        if self.type == PAR_CONTROL:
            s += '(' +  ','.join([str(x) for x in self.parameters]) + ')'
        elif self.type == JUMP_MARK:
            s += ':'
        return s

    def __str__(self):
        return  self.type  + ':' + self.simple_str()

    def __repr__(self):
        return self.__str__()
