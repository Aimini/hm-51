#########################################################
# 2020-01-26 17:23:00
# AI
# ins: ACALL addr11
#########################################################

import __util as u
import random
import itertools
from __asmconst import *
from __numutil import numutil as ntl
from __51util import SIMRAM

p = u.create_test()

def one(count, test_number, p):
    """
    create a return list.
    IRAM have 128 byte, so you can fill most 64 PC value to IRAM.
    """
    instruction_len = 9
    code_page_start_addr = test_number << 11
    fisrt_addr = code_page_start_addr + 3 # reserve space for ljmp
    end_addr = code_page_start_addr + 0x7FA 
    jl = ntl.jl(count)
    start_seg_no = random.choice(jl)
    p += f'''LJMP RET_SEG_{test_number}_{start_seg_no}'''
    p += f''';;;;;;;;;;;;;;;;;;; SEG {test_number}, {hex(code_page_start_addr)}'''
    start_limit_addr = fisrt_addr
    for seg_no, next_seg_no in enumerate(jl):
        end_limit_addr = end_addr - (count - seg_no) * instruction_len # must revseve enough code space from other segment
        addr = random.choice(list(range(start_limit_addr, end_limit_addr + 1)))
        start_limit_addr = addr + instruction_len

        p += f'''
        CSEG AT {hex(addr)}
        RET_SEG_{test_number}_{seg_no}:'''
        if next_seg_no != start_seg_no:
                p += f'''ACALL  RET_SEG_{test_number}_{next_seg_no}'''

        
        p += 'INC A'
        if seg_no == start_seg_no:
            p += f'''
                LJMP RET_SEG_{test_number}_END
                {atl.crash()}
                '''
        else:
            p += f'''
                RET
                {atl.crash()}
                '''
    p += f'RET_SEG_{test_number}_END:'

t = 30
c = 64

for x in range(1, t + 1):
    p += atl.move(SFR_SP, I_FF)
    one(c, x, p)
p += atl.aste(SFR_A, atl.I((t * c) & 0xFF))