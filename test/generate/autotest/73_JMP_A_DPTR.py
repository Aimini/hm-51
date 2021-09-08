#########################################################
# 2020-01-27 12:20:43
# AI
# ins: JMP @A+DPTR
#########################################################

import random

from .. import testutil as u
from ..asmconst import *
from ..numutil import numutil as ntl

p = u.create_test()


def creat_jump_link(p, jump_count, order):
    jmpords = ntl.jl(jump_count)
    start =random.choice(jmpords)
    p += f"""
    LJMP JMP_SEG_{order}_{start}
    """

    for idx,next_idx in enumerate(jmpords):
        p += f"JMP_SEG_{order}_{idx}:"
        if next_idx == start:
            p += f"MOV DPTR, #JMP_SEG_END_{order}"
        else:
            p += f"MOV DPTR, #JMP_SEG_{order}_{next_idx}"
        A = random.getrandbits(8)
        p += f"""
        MOV PSW, 0
        MOV ACC, DPL
        SUBB A, {atl.I(A)}
        MOV DPL, ACC

        MOV  ACC, DPH
        SUBB A, {I_00}
        MOV  DPH, ACC

        MOV ACC, {atl.I(A)}
        JMP @A+DPTR
        """
        #assert always false, bacuase we want jump to oter place.
        p += atl.crash()

    p += f"JMP_SEG_END_{order}:"

creat_jump_link(p, 2214, 0)

