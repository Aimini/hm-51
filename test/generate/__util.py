import argparse
import sys
import pathlib
import io
import atexit
import itertools
import __asmutil as atl
import __asmconst as acst
import inspect
import random

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
        self.is_prepend_clear_reg = True
        self.is_append_dump = True
        self.is_append_exit = True
        def store_file():
            with open(self.filename, "w") as fh:
                fh.write(self.get_content_str())

        atexit.register(store_file)

    def get_content_str(self):
        content = [self.sio.getvalue()]
        if self.is_prepend_clear_reg:
            content.insert(0, atl.clear_reg())
        if self.is_append_dump:
            content.append(atl.dump())
        if self.is_append_exit:
            content.append(atl.exit())
        content.append('END')
        return '\n'.join(content)


    def __iadd__(self, s):
        """
        using as print, but write string to test file.
        """
        self.sio.write(s)
        self.sio.write('\n')
        return self



    @staticmethod
    def riram():
        """
        get range or iram
        """
        return range(0, 0x100)

    @staticmethod
    def rsfr():
        """
        get range of SFR
        """
        return sorted(SFR_MAP.keys())


    @staticmethod
    def rdirect():
        """
        get range of iram and SFR
        """
        return itertools.chain(range(0x80), asm_test.rsfr())

    @staticmethod
    def rbit():
        rsfrbit = [ _ for _ in asm_test.rsfr() if _ % 8 == 0]
        return itertools.chain(range(0x20,0x30), rsfrbit)

        
    def iter_direct(self, f):
        """
        iterate direct address  0 - 255
            f: function
                call f(x, self), x is direct address
        """
      
        for x in self.rdirect():
            f(x, self)

    def iter_iram(self, f):
        """
        iram address
        0 - 256
        """

        for x in self.riram():
            f(x, self)

    def iter_direct_no_psw(self, f):
        """
        iterate iram and SFR in RF.
        """
        for x in self.rdirect():
            if x != 0xD0:
                f(x, self)

    def iterx(self, iter_obj, f):
        """
        provide cross iterator a and b,
        a iterates from front to back,
        b iterates from back to front
        """
        l = len(iter_obj)
        a = list(iter_obj)
        for i, v in enumerate(a):
            f(v, a[l - i - 1], self)

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
            rsf(rs, psw_rs, self)
            for ri in range(2):
                rif(atl.RI(rs,ri),self)

    def iter_rn(self, rsf, rnf):
        """
        iter rn, call function rsf(rs), rnf(rs, rn)
            rsf,rnf: function
                rs between 0 - 4, it's PSW.RS1 and PSW.RS0
                ri between 0 - 8
        """
        for rs in range(4):
            psw_rs = rs << 3
            rsf(rs, psw_rs, self)
            
            for rn in range(8):
                rnf(atl.RN(rs,rn),self)

    def iter_bit(self, f):
        for direct in self.rbit():
            for idx in range(8):
                f(direct,idx, self)

class gaped_addr():
    def __init__(self, start, end, min_gap, count):
        self.start = start
        self.end = end
        self.min_gap = min_gap
        self.count = count

    def __next__(self):
        addr_high_limit = self.end - self.count * self.min_gap
        addr = random.randint(self.start, addr_high_limit)
        self.start = addr + self.min_gap
        self.count -= 1
        return addr

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
