CONTROL = "CONTROL"
JUMP_MARK = "JUMP_MARK"
PAR_CONTROL = "PAR_CONTROL"

class dtoken():
    def __init__(self, lineno, t, v):
        self.lineno = lineno
        self.type = t
        self.value = v
        self.parameters = []
        
    def __str__(self):
        s = "(" + self.type + ": " + self.value
        
        if self.type == "PAR_CONTROL":
            s += '(' +  ','.join([str(x) for x in self.parameters]) + ')'
        s += ")"
        return s
    def __repr__(self):
        return self.__str__()
