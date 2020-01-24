#########################################################
# 2020-01-24 11:16:58
# AI
# ins: JNC offset
#########################################################

import __util as u
import random
from __asmconst import *
from __numutil import numutil as ntl

p = u.create_test()

jump_limit =f"""
; PC = 0
MOV PSW, #00      ; SET PSW TO 0
JNC JMP_LIMIT_127 ; JUMP TO  2 + 0x7F = 0x81
; PC = 2
NOP
; PC = 3
JMP_LIMIT_256:
JNC JMP_SEG_START


CSEG AT 0x81
JMP_LIMIT_127:
JNC JMP_LIMIT_256 ; JUMP TO 0x83 - 0x80 = 0x03
; PC = 0x83

JMP_SEG_START:
"""
p += jump_limit


def creat_jump_link(p, jump_count, order):
    jmpords = ntl.jl(jump_count)
    start =random.choice(jmpords)
    p += f"""
    SJMP JMP_SEG_{order}_{start}
    """
    
    for idx,next_idx in enumerate(jmpords):
        p += f"JMP_SEG_{order}_{idx}:"
        psw = random.getrandbits(8)
        p += atl.move(SFR_PSW,atl.I(psw))
        
        if next_idx == start:
            target = f"JMP_SEG_END_{order}"
        else:
            target = f"JMP_SEG_{order}_{next_idx}"

        if psw & 0x80 == 0:
            p += f"JNC {target}"
            p += atl.astl(I_00, I_00)
        else:
            jump_wrong = f"SEG_WRONG_{order}_{idx}"

            p += f"JNC {jump_wrong}"
            p += f"SJMP {target}"
            p += f"{jump_wrong}:"
            p += atl.astl(I_00, I_00)

    p += f"JMP_SEG_END_{order}:"

for x in range(500):
    creat_jump_link(p, 8,x)

