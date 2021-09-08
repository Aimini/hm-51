#########################################################
# 2020-01-27 14:15:45
# AI
# ins: ACALL addr11
#########################################################

import random

from .. import testutil as u
from ..asmconst import *
from ..numutil import numutil as ntl

p = u.create_test()


def one(start_addr,count, p):
    """
    create a return list.
    IRAM have 128 byte, so you can fill most 64 PC value to IRAM.
    """

    gaddr = u.gaped_addr(start_addr,0xFFD0, 27, count)

    jl = ntl.jl(count)
    start_seg_no = random.choice(jl)

    p += f'''LJMP RET_SEG_{start_seg_no}'''
    for seg_no, next_seg_no in enumerate(jl):
        addr = next(gaddr)
        value = random.getrandbits(8)

        
        a = random.getrandbits(8)
        dptr =(addr - a) & 0xFFFF
        p += f'''
        CSEG AT {hex(addr)}
        DB {hex(value)}
        RET_SEG_{seg_no}:
        MOV ACC, {atl.I(a)}
        MOV DPL, {atl.I(dptr & 0xFF)}
        MOV DPH, {atl.I(dptr >> 8)}
        MOVC A, @A+DPTR
        {atl.aste(SFR_A, atl.I(value))}
        '''
        

        if seg_no == start_seg_no:
            p += f'''
                LJMP RET_SEG_END
                {atl.crash()}
                '''
        else:
            p += f'''
                LJMP  RET_SEG_{next_seg_no}
                {atl.crash()}
                '''
    p += f'RET_SEG_END:'

# init 6 reg,set PSW, init 256 iram
one(6*3 +    3 +      256*(3 + 2), 2000, p)
p += atl.clear_reg()