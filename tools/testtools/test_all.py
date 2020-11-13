#########################################################
# scan all test fille in <dir>
#########################################################

import asyncio
import sys
import pathlib
import os

from concurrent.futures import ThreadPoolExecutor, as_completed
from test_process import test_process
import io
import threading
import signal


args = sys.argv[1:]
#args = ['gen_test', 'temp']
usage = '''
test_all.py <script_dir> <temp_dir> <thread_count>
    scan all generate script file in <script_dir> and run it. the file name start with '__' will be ignored.

    script_dir: the directory contains all test generate script. 
    temp_dir: the temporary directory.
'''
if len(args) < 3:
    print(usage)
    exit(1)

script_dir = args[0]  # pathlib.Path(sys.argv[1])
temp_dir = args[1]  # pathlib.Path(sys.argv[2])
executor_cnt = int(args[2])
print_lock = threading.Lock()

ignored_file = {'__51util.py', '__asmconst.py', '__asmutil.py', '__numutil.py', '__util.py',
                'man_assert_check.py', 'int_test.py',
                'INS_XXX_A_d.py', 'INS_XXX_A_i.py', 'INS_XXX_A_Ri.py', 'INS_XXX_A_Rn.py',
                'INS_OPERATION.py'}



def create_subprocess(fullpathname, temp_dir):
    tp = test_process(fullpathname, temp_dir)
    tp.addflag(test_process.F_NEW_ASM).addflag(test_process.F_NEW_HEX)\
    .addflag(test_process.F_SIM_INSTRUCTION).addflag(test_process.F_SIM_CIRCUIT)\
    .addflag(test_process.F_VERIFY)

    with print_lock:
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        print('>>>> test:{}'.format(fullpathname))

    return tp.run(), fullpathname, tp.output


def main(executor):
    tasks = []
    find_debug = False
    for filename in os.listdir(script_dir):
        #if filename == '93_MOVC_A_A_DPTR.py':
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
        tsk = executor.submit(create_subprocess, fullpathname, temp_dir)
        tasks.append(tsk)


    
    def cancel_executor():
        for t in tasks:
            t.cancel()
        executor.shutdown()

    def int_cacel(signum, frame):
        cancel_executor()

    signal.signal(signal.SIGINT, int_cacel)                                


    for future in as_completed(tasks):
        retcode, filename, output = future.result()
        if retcode != 0:
            cancel_executor()
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            print(output.decode('utf-8'))
            print('error at file {!r}'.format(filename))
            break
    print('total test:', len(tasks))

if __name__ == '__main__':
    executor = ThreadPoolExecutor(max_workers=executor_cnt)
    main(executor)

    


