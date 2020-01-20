from __numutil import numutil

class HV():
    """"hex value class"""
    def __init__(self,x, l = 2):
        self.x = x
        self.l = l

    def __str__(self):
         return ("0x{:0>" + str(self.l) + "X}").format(self.x)


class I(HV):
    """
    8bit immed
    """
    def __init__(self,x,l = 2):
        super().__init__(x,l)

    def __str__(self):
         return "#" + super().__str__()


class D(HV):
    """
    direct address
    """
    def __init__(self,x):
        super().__init__(x,2)

def move(dest,src):
    return f"MOV {dest},{src}"

def ins(*args):
    '''
    convert a list of instruction name and args to instrcution string.
        example:
            if args is ["MOV","A","#0x11"]
            then return is "MOV A,#0x11"
        args: *
            a var parameters of string
        return:str
            instruction string
    '''
    return args[0] + ' ' + ', '.join([str(_) for _ in args[1:]])

def exit():
    """
    return string of instructions that exit from Digitalc.exe.
        src: int, D, I
            exit code source, can be a immed(I) or direct address(int, D),default is exit with immediate 0.
    """
    return move(D(0xFC), 1)

def ast(a,b,func):
    """
    return string of instructions that excute assert function.
        a: str,int,D,I
            value0
        b: str,int,D,I
            value1
        func: int
            0x01 a > b
            0x02 a = b
            0x03 a < b

    """
    return """
MOV 0xFD, {}
MOV 0xFE, {}
MOV 0xFF, {}
""".format(a,b,func)

def brk():
    """
    return string of instructions that make a break
    """
    return "MOV 0xFD, 0"
    
def astl(a,b):
    """
    return string of instructions that assert a < b.
    """
    return f";;;;;;;;;;;; assert {a} < {b} \n" + ast(a,b,I(3))

def aste(a,b):
    """
    return string of instructions that assert a = b.
    """
    return f";;;;;;;;;;;; assert {a} == {b} \n" + ast(a,b,I(2))

def astg(a,b):
    """
    return string of instructions that assert a > b.
    """
    return f";;;;;;;;;;;; assert {a} > {b} \n" + ast(a,b,I(1))

reg_A = "A"
reg_B = "B"
reg_IE = "IE"
reg_IP = "IP"