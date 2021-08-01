#########################################################
# 2020-01-24 11:16:58
# AI
# ins: JZ offset
#########################################################

import random

from .. import testutil as u
from ..asmconst import *
from ..numutil import numutil as ntl

p = u.create_test()
p.is_prepend_clear_reg = False
p.is_prepend_clear_iram = False

jump_limit =f"""
; PC = 0
MOV ACC, #0      ; SET　 A TO 0
JZ JMP_LIMIT_127 ; JUMP TO  2 + 0x7F = 0x81
; PC = 2
NOP
; PC = 3
JMP_LIMIT_256:
JZ JMP_SEG_START


CSEG AT 0x81
JMP_LIMIT_127:
JZ JMP_LIMIT_256 ; JUMP TO 0x83 - 0x80 = 0x03
; PC = 0x83

JMP_SEG_START:
"""
p += jump_limit
p += atl.clear_iram()
p += atl.clear_reg()


def creat_jump_link(p, jump_count, order):
    jmpords = ntl.jl(jump_count)
    start =random.choice(jmpords)
    p += f"""
    SJMP JMP_SEG_{order}_{start}
    """
    
    for idx,next_idx in enumerate(jmpords):
        p += f"JMP_SEG_{order}_{idx}:"
        A = random.getrandbits(8)
        p += atl.move(SFR_A,atl.I(A))
        
        if next_idx == start:
            target = f"JMP_SEG_END_{order}"
        else:
            target = f"JMP_SEG_{order}_{next_idx}"

        if A == 0:
            p += f"JZ {target}"
            p += atl.crash()
        else:
            jump_wrong = f"SEG_WRONG_{order}_{idx}"

            p += f"JZ {jump_wrong}"
            p += f"SJMP {target}"
            p += f"{jump_wrong}:"
            p += atl.crash()

    p += f"JMP_SEG_END_{order}:"

for x in range(500):
    creat_jump_link(p, 8,x)

