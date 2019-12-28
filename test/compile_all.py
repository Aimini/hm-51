import subprocess
import sys
import pathlib
"""
usage:
    compile_all <input_file> <output_dir>
    input_file is 51 assembly file
    ouput_dir is used to store ouput file,it's an intel hex format file, and it have the same name as input file.
"""
def asmobj(filenamestr, tempdirstr):
    filename =  pathlib.Path(filenamestr)
    tempdir = pathlib.Path(tempdirstr)
    filestem = filename.stem
    objfile =  tempdir / (filestem + ".obj")
    subprocess.run(f"A51 {filename} OBJECT({objfile})")
    absfile =  tempdir / (filestem + ".abs")
    subprocess.run(f"BL51 {objfile} TO {absfile}")
    hexfile =  tempdir / (filestem + ".hex")
    subprocess.run(f"OH51 {absfile}  HEXfile({hexfile})")
    

if len(sys.argv) < 2:
    print("[error] assembly filename missing")
else:
    asmobj(sys.argv[1], sys.argv[2])