import argparse
import sys
import pathlib
import __asmutil as atl


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
    """
    direct address
    0 - 255
    """
    for x in range(256):
        f(x)

def iram(f):
    """
    iram address
    0 - 127
    """
    for x in range(128):
        f(x)


def sdirect(f):
    """
    sdirect address, include iram and sfr than in RF.
    """
    iram(f)
    for k in sorted(SFR_MAP.keys()):
        f(k)

def test(do):
    """
    provide command line configuration and create test .A51 file to target directory,
    .A51 file have the same name as the .py script file. It's also add exit code and 
    'END' macro in .A51 file.
        do: (write: function)->None
            a callback function than accept a function write,
            write will write a string to .A51 file but add '\n' after each write.
    """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-o', '--output-dir', action='store', type=str, dest='output_dir', default='.')
    op = arg_parser.parse_args(sys.argv[1:])
    ofilepath = pathlib.Path(op.output_dir) / (pathlib.Path(sys.argv[0]).stem + ".A51")
    print(ofilepath)

    lines = []
    do(lambda s: lines.append(s))

    lines.append(atl.exit())
    lines.append("END")
    with open(ofilepath,"w") as fh:

        fh.writelines([_ + '\n' for _ in lines])


