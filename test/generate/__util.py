import argparse
import sys
import pathlib
import __numutil
SFR_MAP = {
    0x81:2,#"SP"],
    0x82:4,#"DPL"],
    0x83:5,#"DPH"],
    0xA8:6,#"IE"],
    0xB8:7,#"IP"],
    0xD0:3,#"PSW"],
    0xE0:0,#"A"],
    0xF0:1,#"B"],
}
def direct(f):
    for x in range(256):
        f(x)

def iram(f):
    for x in range(128):
        f(x)


def sdirect(f):
    iram(f)
    for k in sorted(SFR_MAP.keys()):
        f(k)

def test(do):
    """
    create test asm file to dir, filename is same as test name 
    """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-o', '--output-dir', action='store', type=str, dest='output_dir', default='.')
    op = arg_parser.parse_args(sys.argv[1:])
    ofilepath = pathlib.Path(op.output_dir) / (pathlib.Path(sys.argv[0]).stem + ".A51")
    print(ofilepath)
    with open(ofilepath,"w") as fh:
        do(fh,fh.write)

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
    return args[0] + ' ' + ','.join(args[1:])


class numutil(__numutil.numutil):
    @staticmethod
    def immed(x):
        return "#" + numutil.sx2(x)

    @staticmethod
    def direct(x):
        return numutil.sx2(x)