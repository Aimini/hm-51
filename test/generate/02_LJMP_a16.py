#########################################################
# 2020-01-24 11:16:58
# AI
# ins: LJMP offset
#########################################################

import __util as u
import random
from __asmconst import *
from __numutil import numutil as ntl

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
            p += f"LJMP JMP_SEG_END_{order}"
        else:
            p += f"LJMP JMP_SEG_{order}_{next_idx}"
        #assert always false, bacuase we want jump to oter place.
        p += atl.astl(I_00,I_00)

    p += f"JMP_SEG_END_{order}:"

creat_jump_link(p, 5459, 0)

