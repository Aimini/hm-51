#########################################################
# 2020-01-26 22:00:45
# AI
# ins: AJMP addr11
#########################################################

import random

from .. import testutil as u
from ..asmconst import *
from ..numutil import numutil as ntl

p = u.create_test()


def one(count, test_number, p):
    """
    create a return list.
    IRAM have 128 byte, so you can fill most 64 PC value to IRAM.
    """
    instruction_len = 5
    code_page_start_addr = test_number << 11
    fisrt_addr = code_page_start_addr + 3  # reserve space for ljmp
    end_addr = code_page_start_addr + 0x7FA
    jl = ntl.jl(count)

    start_seg_no = random.choice(jl)
    p += f'''LJMP RET_SEG_{test_number}_{start_seg_no}'''
    p += f''';;;;;;;;;;;;;;;;;;; SEG {test_number}, {hex(code_page_start_addr)}'''
    start_limit_addr = fisrt_addr

    for seg_no, next_seg_no in enumerate(jl):
        # must revseve enough code space from other segment
        end_limit_addr = end_addr - (count - seg_no) * instruction_len
        addr = random.choice(list(range(start_limit_addr, end_limit_addr + 1)))
        start_limit_addr = addr + instruction_len

        p += f'''
        CSEG AT {hex(addr)}
        RET_SEG_{test_number}_{seg_no}:'''
        if next_seg_no != start_seg_no:
            target = f'RET_SEG_{test_number}_{next_seg_no}'
        else:
            target = f'RET_SEG_{test_number}_END'

        p += f'''
        AJMP  {target}
        {atl.crash()}
        '''

    p += f'RET_SEG_{test_number}_END:'


t = 30
c = 64

for x in range(1, t + 1):
    one(c, x, p)
