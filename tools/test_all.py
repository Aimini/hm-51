#########################################################
# scan all test fille in <dir>
#########################################################

import subprocess
import sys
import pathlib
import os

from concurrent.futures import ThreadPoolExecutor, as_completed

import io
import threading
import signal


args = sys.argv[1:]
#args = ['gen_test', 'temp']
usage = '''
test_one.py <script_dir> <temp_dir>
    scan all generate script file in <script_dir> and run it. the file name start with '__' will be ignored.

    script_dir: the directory contains all test generate script. 
    temp_dir: the temporary directory.
'''
if len(args) < 2:
    print(usage)
    exit(1)

script_dir = args[0]  # pathlib.Path(sys.argv[1])
temp_dir = args[1]  # pathlib.Path(sys.argv[2])
p = R'python tools\test_one.py {} {}'
print_lock = threading.Lock()

ignored_file = {'__51util.py', '__asmconst.py', '__asmutil.py', '__numutil.py', '__util.py',
                'man_assert_check.py', 'int_test.py',
                'INS_XXX_A_d.py', 'INS_XXX_A_i.py', 'INS_XXX_A_Ri.py', 'INS_XXX_A_Rn.py',
                'INS_OPERATION.py'}


def create_subprocess(name):
    with print_lock:
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        print('>>>> test:{}'.format(name))
    p = subprocess.Popen(name, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutdata, stderrdata = p.communicate('')
    return p, name, stdoutdata, stderrdata


if __name__ == '__main__':
    pool = ThreadPoolExecutor(max_workers=5)

    tasks = []
    find_debug = False
    for filename in os.listdir(script_dir):
        # if filename == 'F6_F7_MOV_Ri_A.py':
        find_debug = True

        if filename in ignored_file:
            continue

        if not find_debug:
            continue

        if filename.startswith('__'):
            continue

        fullpathname = os.path.join(script_dir, filename)
        if not os.path.isfile(fullpathname):
            continue

        cmd = p.format(fullpathname, temp_dir)
        r = pool.submit(create_subprocess, cmd)
        tasks.append(r)

    def cancel_all():
        for one in tasks:
            if not one.running() and not one.cancelled():
                one.cancel()

    def int_cacel(signum, frame):
        cancel_all()

    signal.signal(signal.SIGINT, int_cacel)                                

    for future in as_completed(tasks):
        ret, name, stdout, stderr = future.result()
        if ret.returncode != 0:
            with print_lock:
                print('error:', name)
                print(stdout.decode('utf-8'))
                print(stderr.decode('utf-8'))
            cancel_all()
            exit(-1)
    print('total test:', len(tasks))
    exit(0)
