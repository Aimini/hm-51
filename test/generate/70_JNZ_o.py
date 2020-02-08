#########################################################
# 2020-01-24 11:16:58
# AI
# ins: JNZ offset
#########################################################

import __util as u
import random
from __asmconst import *
from __numutil import numutil as ntl

p = u.create_test()

jump_limit =f"""
; PC = 0
MOV ACC, #0xFF      ; SET A TO 0xFF
JNZ JMP_LIMIT_127 ; JUMP TO  2 + 0x7F = 0x81
; PC = 2
NOP
; PC = 3
JMP_LIMIT_256:
JNZ JMP_SEG_START


CSEG AT 0x81
JMP_LIMIT_127:
JNZ JMP_LIMIT_256 ; JUMP TO 0x83 - 0x80 = 0x03
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
        A = random.getrandbits(8)
        p += atl.move(SFR_A,atl.I(A))
        
        if next_idx == start:
            target = f"JMP_SEG_END_{order}"
        else:
            target = f"JMP_SEG_{order}_{next_idx}"

        if A != 0:
            p += f"JNZ {target}"
            p += atl.crash()
        else:
            jump_wrong = f"SEG_WRONG_{order}_{idx}"

            p += f"JNZ {jump_wrong}"
            p += f"SJMP {target}"
            p += f"{jump_wrong}:"
            p += atl.crash()

    p += f"JMP_SEG_END_{order}:"

for x in range(500):
    creat_jump_link(p, 8,x)

