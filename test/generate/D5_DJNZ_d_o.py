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
    for addr in p.rdirect():
        value = random.getrandbits(8)
        p += atl.move(atl.D(addr),atl.I(value))
        ram.set_direct(addr, value)

def creat_jump_link(p, jump_count, order):
    init_ram(p)

    jumpords = list(range(jump_count))
    random.shuffle(jumpords)
    segcode = ['' for _ in range(jump_count)]
    start =jumpords[0]

    p += f"""
    SJMP JMP_SEG_{order}_{start}
    """
    ris = list(p.rdirect())
    for i, idx in enumerate(jumpords):
        segcode[idx] += f"JMP_SEG_{order}_{idx}:\n"
        
        addr = random.choice(ris)
        value = (ram.get_direct(addr) - 1) & 0xFF
        ram.set_direct(addr, value)

        if i < len(jumpords) - 1:
            next_idx = jumpords[i + 1]
            target = f"JMP_SEG_{order}_{next_idx}\n"
        else:
            target = f"JMP_SEG_END_{order}\n"

        if value != 0:
            segcode[idx] += f"DJNZ {atl.D(addr)}, {target}\n"
            segcode[idx] += atl.crash() + '\n'
        else:
            jump_wrong = f"SEG_WRONG_{order}_{idx}"

            segcode[idx] += f"DJNZ {atl.D(addr)}, {jump_wrong}\n"
            segcode[idx] += f"SJMP {target}\n"
            segcode[idx] += f"{jump_wrong}:\n"
            segcode[idx] += atl.crash() + '\n'
    p += '\n'.join(segcode)
    p += f"JMP_SEG_END_{order}:"

for x in range(110):
    creat_jump_link(p, 7,x)

