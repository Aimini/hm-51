#########################################################
# 2020-01-26 15:03:43
# AI
# ins: RET
#########################################################

import __util as u
import random
import itertools
from __asmconst import *
from __numutil import numutil as ntl
from __51util import SIMRAM

p = u.create_test()
SP = 0xFF
p += atl.move(SFR_SP, atl.I(SP))


def one(count, test_number, p):
    """
    create a return list.
    IRAM have 128 byte, so you can fill most 64 PC value to IRAM.
    """

    jl = ntl.jl(count)
    start_seg_no = random.choice(jl)
    p += f'LJMP RET_SEG_{count}_{start_seg_no}'

    for seg_no, next_seg_no in enumerate(jl):
        
        SP = random.choice(list(range(0x1,0x80)))
        
        if next_seg_no == start_seg_no:
            next_seg_label = f'RET_SEG_{count}_END'
        else:
            next_seg_label = f'RET_SEG_{count}_{next_seg_no}'

        p += f'''
        RET_SEG_{count}_{seg_no}:
            MOV DPTR, #{next_seg_label}
            MOV SP, {atl.I(SP)}
            MOV {atl.D(SP)}, DPH
            MOV {atl.D(SP - 1)}, DPL
            RET
            {atl.crash()}
        '''
    p += f'RET_SEG_{count}_END:'


one(4000, 0, p)