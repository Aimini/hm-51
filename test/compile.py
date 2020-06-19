import subprocess
import sys
import pathlib
import os
import random
import string
class trysubp():
    """
    provide subprocess chain, if one subprocess in chain return code is not 0,
    then subprocess will stop excute consecutive subprocesses.
    usage:
        ret = trysubp.build(arg_to_subprocess0)
            .chain(arg_to_subprocess1)
            .chain(arg_to_subprocess1)
            .chain(arg_to_subprocess1)
            .chain(arg_to_subprocess1)
            ...
        ret is the failed subprocess(if have, you can check ret's return code)
    """
    def __init__(self,*args, **kargs):
        """
        args, kargs:
            arguments pass to subprocess
        """
        self.returncode = subprocess.run(*args, **kargs).returncode


    def chain(self, *args, **kargs):
        if self.returncode == 0:
            return trysubp(*args, **kargs)
        else:
            return self


def compile(inputfile_str, outputfile_str):
    inputfile = pathlib.Path(inputfile_str)
    outputfile = pathlib.Path(outputfile_str)
    tempdir = outputfile.parent
    filestem = outputfile.stem

    objfile =  tempdir  / (filestem + ".obj")
    absfile =  tempdir  / (filestem + ".abs")
    hexfile =  tempdir  / (filestem + ".hex")
    tooldir = pathlib.Path(R"C:\Keil_v5\C51\BIN")
    A51 = tooldir / 'A51.exe'
    BL51 = tooldir / 'BL51.exe'
    OH51 = tooldir / 'OH51.exe'
    # create a unique dir for BL51
    # Since the damned BL51 always uses the same temporary file name, 
    # there is a possibility that two BL51.exe will conflict when working at the same time.
    BL_temp_dir_str = '__' + ''.join(random.sample(string.ascii_letters + string.digits, 16))
    BL_abs_temp_dir_str = str((tempdir / BL_temp_dir_str).absolute())
    os.mkdir(BL_abs_temp_dir_str)
    evn_BL51 = os.environ.copy()
    evn_BL51["TMP"] = BL_abs_temp_dir_str
    rp = trysubp(f"{A51} {inputfile} OBJECT({objfile})")\
        .chain(f"{BL51} {objfile} TO {absfile}", env=evn_BL51)\
        .chain(f"{OH51} {absfile}  HEXfile({hexfile})")

    return rp.returncode




usage = """
usage:
    compile_all <input_file> <output_file>
    input_file:
        51 assembly file
    output_file:
        output file,it's an intel hex format file
"""

if len(sys.argv) < 3:
    print(usage)
else:
    t = compile(sys.argv[1], sys.argv[2])
    print("program exit with code {}.".format(t))
    exit(t)