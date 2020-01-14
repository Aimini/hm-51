import argparse
import sys
import pathlib
import io
import atexit

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

class asm_test:
    def __init__(self, filename):
        self.filename = filename
        self.sio = io.StringIO()
        def store_file():
            with open(self.filename, "w") as fh:
                fh.writelines(self.sio.getvalue())

        atexit.register(store_file)

    def __call__(self,* vargs, **kargs):
        """
        using as print, but write string to test file.
        """
        print(*vargs, file = self.sio, **kargs)
       
    def iter_direct(self, f):
        """
        iterate direct address  0 - 255
            f: function
                call f(x), x is direct address
        """
        for x in range(256):
            self(f(x))

    def iter_iram(self, f):
        """
        iram address
        0 - 127
        """
        for x in range(128):
            self(f(x))


    def iter_is(self,f):
        """
        iterate iram and SFR in RF.
        """
        self.iter_iram(f)
        for k in sorted(SFR_MAP.keys()):
            self(f(k))



def create_test():
    """
    provide command line configuration and create test .A51 file to target directory
    .A51 file have the same name as the .py script file. It's also add exit code and 
    'END' macro in .A51 file.

    you have two way to create test:

        1. using function callback  as parameter <do>. In callback function you should using first
        paramter as a function, using it to write text.
        2. using None as parameter <do>: it will add a function asm_p to builtins module,then you 
        can using asmpt as predefined function that wirte text to test file. It's work like print.

    parameters:
        do: (write: function)->None
            a callback function than accept a function write,
            write will write a string to .A51 file but add '\\n' after each write.
            
            if it's None, please use asmpt like print
    """
    # parse argument
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-o', '--output-dir', action='store', type=str, dest='output_dir', default='.')
    op = arg_parser.parse_args(sys.argv[1:])
    ofilepath = pathlib.Path(op.output_dir) / (pathlib.Path(sys.argv[0]).stem + ".A51")

    return asm_test(ofilepath)





