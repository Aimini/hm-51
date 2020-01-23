import argparse
import sys
import pathlib
import io
import atexit
import itertools
import __asmutil as atl
import __asmconst as acst
import inspect
SFR_MAP = {
    0x81: 2,  # "SP"],
    0x82: 4,  # "DPL"],
    0x83: 5,  # "DPH"],
    0xA8: 6,  # "IE"],
    0xB8: 7,  # "IP"],
    0xD0: 3,  # "PSW"],
    0xE0: 0,  # "A"],
    0xF0: 1,  # "B"],
}


class asm_test:
    def __init__(self, filename):
        self.filename = filename
        self.sio = io.StringIO()

        def store_file():
            with open(self.filename, "w") as fh:
                fh.write('\n'.join([
                    atl.clear_reg(),
                    self.sio.getvalue(),
                    atl.dump(),
                    atl.exit(),
                    'END']))

        atexit.register(store_file)

    def __call__(self, * vargs, **kargs):
        """
        using as print, but write string to test file.
        """
        print(*vargs, file=self.sio, **kargs)

    def __iadd__(self, s):
        """
        using as print, but write string to test file.
        """
        self(s)
        return self

    @staticmethod
    def rdirect():
        """
        get range or direct
        """
        return range(0, 0x100)

    @staticmethod
    def riram():
        """
        get range or iram
        """
        return range(0, 0x80)

    @staticmethod
    def rsfr():
        """
        get range of SFR
        """
        return sorted(SFR_MAP.keys())

    @staticmethod
    def ris():
        """
        get range of iram and SFR
        """
        return itertools.chain(asm_test.riram(), asm_test.rsfr())


    def pass_by_len(self, f, *args):
        if len(inspect.signature(f).parameters) == len(args):
            self(f(*args))
        else:
            self(f(*args, self))
        
    def iter_direct(self, f):
        """
        iterate direct address  0 - 255
            f: function
                call f(x), x is direct address
        """
      
        for x in self.rdirect():
            self.pass_by_len(f, x)

    def iter_iram(self, f):
        """
        iram address
        0 - 127
        """

        for x in self.riram():
            self.pass_by_len(f, x)

    def iter_is(self, f):
        """
        iterate iram and SFR in RF.
        """
        for x in self.ris():
            self.pass_by_len(f, x)

    def iter_is_no_psw(self, f):
        """
        iterate iram and SFR in RF.
        """
        self.iter_iram(f)
        for x in self.rsfr():
            if x != 0xD0:
                self.pass_by_len(f, x)

    def iterx(self, iter_obj, f):
        """
        provide cross iterator a and b,
        a iterates from front to back,
        b iterates from back to front
        """
        l = len(iter_obj)
        a = list(iter_obj)
        for i, v in enumerate(a):
            self.pass_by_len(f, v, a[l - i - 1])

    def iterx_iram(self, f):
        """
        cross iter iram, see iterx in asm_test
        """
        self.iterx(self.riram(), f)

    def iterx_sfr(self, f):
        """
        cross iter iram, see iterx in asm_test
        """
        self.iterx(self.rsfr(), f)

    def iterx_is(self, f):
        """
        cross iter iram and SFR, see iterx in asm_test
        """
        self.iterx(self.ris(), f)
    
    def iter_ri(self, rsf, rif):
        """
        iter ri, call function(rs, ri)
            f: function
                rs between 0 - 3, it's PSW.RS1 and PSW.RS0
                ri between 0 - 1
        """
        for rs in range(4):
            psw_rs = rs << 3
            self.pass_by_len(rsf, rs, psw_rs)
            for ri in range(2):
                self.pass_by_len(rif, atl.RI(rs,ri))

    def iter_rn(self, rsf, rnf):
        """
        iter rn, call function rsf(rs), rnf(rs, rn)
            rsf,rnf: function
                rs between 0 - 4, it's PSW.RS1 and PSW.RS0
                ri between 0 - 8
        """
        for rs in range(4):
            psw_rs = rs << 3
            self.pass_by_len(rsf, rs, psw_rs)
            
            for rn in range(8):
                self.pass_by_len(rnf, atl.RN(rs,rn))


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
