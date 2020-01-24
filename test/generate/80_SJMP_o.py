#########################################################
# 2020-01-24 11:16:58
# AI
# ins: SJMP offset
#########################################################

import __util as u
import random
from __asmconst import *
from __numutil import numutil as ntl

p = u.create_test()

jump_limit =f"""
; PC = 0
SJMP JMP_LIMIT_127 ; JUMP TO  2 + 0x7F = 0x81
; PC = 2
NOP
; PC = 3
JMP_LIMIT_256:
SJMP JMP_SEG_START
{atl.astl(I_00,I_00)}

CSEG AT 0x81
JMP_LIMIT_127:
SJMP JMP_LIMIT_256 ; JUMP TO 0x83 - 0x80 = 0x03
; PC = 0x83
{atl.astl(I_00,I_00)}
JMP_SEG_START:
"""
p += jump_limit


def creat_jump_link(jump_count, order):
    jmpords = ntl.jl(jump_count)
    start =random.choice(jmpords)
    global p
    p += f"""
    SJMP JMP_SEG_{order}_{start}
    """

    for idx,next_idx in enumerate(jmpords):
        p += f"JMP_SEG_{order}_{idx}:"
        if next_idx == start:
            p += f"SJMP JMP_SEG_END_{order}"
        else:
            p += f"SJMP JMP_SEG_{order}_{next_idx}"
        #assert always false, bacuase we want jump to oter place.
        p += atl.astl(I_00,I_00)

    p += f"JMP_SEG_END_{order}:"

for x in range(500):
    creat_jump_link(11,x)