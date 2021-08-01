#########################################################
# scan all test fille in <dir>
#########################################################

import asyncio
import sys
import io

from concurrent.futures import ThreadPoolExecutor, as_completed
from test_process import test_process
import pkgutil
import threading
import signal
from testconfig import auto_tester_pkgname



usage = '''
test_all.py <script_dir> <temp_dir> <thread_count>
    scan all generate script file in <script_dir> and run it. the file name start with '__' will be ignored.

    script_dir: the directory contains all test generate script. 
    temp_dir: the temporary directory.
'''


args = sys.argv[1:]
if len(args) < 2:
    print(usage)
    exit(1)

temp_dir = args[0]  # pathlib.Path(sys.argv[2])
executor_cnt = int(args[1])
print_lock = threading.Lock()

ignored_tester_name = {}



def create_subprocess(tester_name, temp_dir):
    output_file = io.StringIO()
    tp = test_process(tester_name, temp_dir, output_file)
    tp.addflag(test_process.F_NEW_ASM).addflag(test_process.F_NEW_HEX)\
    .addflag(test_process.F_SIM_INSTRUCTION).addflag(test_process.F_SIM_CIRCUIT)\
    .addflag(test_process.F_VERIFY)

    
    with print_lock:
        print('>>>> begin test: {}'.format(tester_name))

    return tp.run(), tester_name, output_file


def main(executor):
    tasks = []
    find_debug = False
    for testermodule in pkgutil.iter_modules([auto_tester_pkgname]):
        if testermodule.ispkg:
            continue
        #if filename == '93_MOVC_A_A_DPTR.py':
        find_debug = True

        if testermodule.name in ignored_tester_name:
            continue

        if not find_debug:
            continue



        tsk = executor.submit(create_subprocess, testermodule.name, temp_dir)
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
            print(output.getvalue())
            print('error at file "{}\\{}.py"'.format(auto_tester_pkgname,filename))
            break
    print('total test:', len(tasks))

if __name__ == '__main__':
    executor = ThreadPoolExecutor(max_workers=executor_cnt)
    main(executor)

    


