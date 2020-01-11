import subprocess
import sys
import pathlib
usage = """
usage:
    compile_all <input_file> <output_dir>
    input_file:
        51 assembly file
    ouput_dir:
        directory to store output file,it's an intel hex format file, and it have the same name as input file.
"""
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

def asmobj(filenamestr, tempdirstr):
    filename =  pathlib.Path(filenamestr)
    tempdir = pathlib.Path(tempdirstr)
    filestem = filename.stem

    objfile =  tempdir / (filestem + ".obj")
    absfile =  tempdir / (filestem + ".abs")
    hexfile =  tempdir / (filestem + ".hex")

    rp = trysubp(f"A51 {filename} OBJECT({objfile})")\
    .chain(f"BL51 {objfile} TO {absfile}")\
    .chain(f"OH51 {absfile}  HEXfile({hexfile})")
    
    return rp.returncode

if len(sys.argv) < 3:
    print(usage)
else:
    ec = asmobj(sys.argv[1], sys.argv[2])
    print()
    print("program exit with code {}.".format(ec))
    exit(ec)