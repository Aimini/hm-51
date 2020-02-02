#########################################################
# 2020-01-28 19:29:22
# AI
# ins: DJNZ direct, offset
#########################################################

import __util as u
import random
import itertools
from __asmconst import *
from __numutil import numutil as ntl
from __51util import SIMRAM
p = u.create_test()
ram = SIMRAM()


def init_ram(p):
    for addr in p.ris():
        value = random.getrandbits(8)
        p += atl.move(atl.D(addr),atl.I(value))
        ram.set_direct(addr, value)

def creat_jump_link(p, jump_count, order):
    init_ram(p)

    jmpords = ntl.jl(jump_count)
    start =random.choice(jmpords)

    p += f"""
    SJMP JMP_SEG_{order}_{start}
    """
    ris = list(p.ris())
    for idx,next_idx in enumerate(jmpords):
        p += f"JMP_SEG_{order}_{idx}:"
        
        addr = random.choice(ris)
        value = (ram.get_direct(addr) - 1) & 0xFF
        ram.set_direct(addr, value)

        if next_idx == start:
            target = f"JMP_SEG_END_{order}"
        else:
            target = f"JMP_SEG_{order}_{next_idx}"

        if value != 0:
            p += f"DJNZ {atl.D(addr)}, {target}"
            p += atl.crash()
        else:
            jump_wrong = f"SEG_WRONG_{order}_{idx}"

            p += f"DJNZ {atl.D(addr)}, {jump_wrong}"
            p += f"SJMP {target}"
            p += f"{jump_wrong}:"
            p += atl.crash()

    p += f"JMP_SEG_END_{order}:"

for x in range(110):
    creat_jump_link(p, 7,x)

