#########################################################
# begin a test from generate script in /test/generate
#########################################################

import subprocess
import sys
import pathlib

usage = """
    test_one.py <generate_srcipt> <temp_dir>
        generate_script: the .py file in /src/test/generate directory, test_one.py will run it to generate asm file, then invoke /test/compile_verify.py to run compile-simulate-verify process, all itermidate file will store in temp_dir
        temp_dir: the temporary directory.
"""
if len(sys.argv) < 3:
    print(usage)
    exit(1)

generate_srcipt = pathlib.Path(sys.argv[1])
temp_dir = pathlib.Path(sys.argv[2])
p = R"test\compile_verify.py"

a = subprocess.run(['python', generate_srcipt, '-o',temp_dir])
if a.returncode != 0:
    print('error in genrate script "{}"'.format(generate_srcipt))
    exit(a.returncode)

a = subprocess.run(['python', p, temp_dir / (generate_srcipt.stem + ".A51"), temp_dir])
exit(a.returncode)