import subprocess
import sys
import pathlib
def asmobj(strfilename, filedir, tempdir):
    filename =  pathlib.Path(filedir) / strfilename
    filestem = filename.stem
    outputfilename =  pathlib.Path(tempdir) / (filestem + ".obj")
    subprocess.run(f"A51 {filename} OBJECT({outputfilename})")

if len(sys.argv) < 2:
    print("[error] assembly filename missing")
else:
    asmobj(sys.argv[1], R"test\src", R"test\temp")