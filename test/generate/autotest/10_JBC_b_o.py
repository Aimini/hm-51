#########################################################
# 2020-01-25 21:00:29
# AI
# ins: JBC bit, offset
#########################################################

import itertools
import random

from .. import testutil as u
from ..sim51util import SIMRAM
from ..asmconst import *

p = u.create_test()
p.is_prepend_clear_reg = False
p.is_prepend_clear_iram = False
ram = SIMRAM()

jump_limit = f"""
; PC = 0
MOV 0xE0, #0xFF      ; SET A TO 0x80
JBC 0xE0.0, JMP_LIMIT_127 ; JUMP TO  2 + 0x7F = 0x81
; PC = 2
NOP
; PC = 3
JMP_LIMIT_256:
JBC 0xE0.2, JMP_SEG_START


CSEG AT 0x81
JMP_LIMIT_127:
JBC 0xE0.1,JMP_LIMIT_256 ; JUMP TO 0x83 - 0x80 = 0x03
; PC = 0x83

JMP_SEG_START:
"""
p += jump_limit
p += atl.clear_iram()
p += atl.clear_reg()


def random_bit(x):
    yield random.choice(list(p.rbit()))


valueiter = itertools.chain(p.rbit(), itertools.cycle(random_bit(8)))


def creat_jump_link(p, jump_count, order):
    jump_link = list(range(jump_count))
    random.shuffle(jump_link)
    jump_seg_str = list(range(jump_count))

    start = jump_link[0]

    p += f'SJMP JMP_SEG_{order}_{start}'

    for idx in range(len(jump_link)):
        current_seg_no = jump_link[idx]
        next_seg_no = jump_link[(idx + 1)% len(jump_link)]

        seg_str_list = []
        seg_str_list.append(f"JMP_SEG_{order}_{current_seg_no}:")

        bit_idx = random.getrandbits(3)
        addr = next(valueiter)

        B = atl.BIT(addr, bit_idx)

        if idx == len(jump_link) - 1:
            target = f"JMP_SEG_END_{order}"
        else:
            target = f"JMP_SEG_{order}_{next_seg_no}"

        if ram.get_bit(addr, bit_idx) > 0:
            seg_str_list.append(f"JBC {B}, {target}")
            seg_str_list.append(atl.crash())
        else:
            jump_wrong = f"SEG_WRONG_{order}_{idx}"

            seg_str_list.append(f"JBC {B}, {jump_wrong}")
            seg_str_list.append(f"SJMP {target}")
            seg_str_list.append(f"{jump_wrong}:")
            seg_str_list.append(atl.crash())

        jump_seg_str[current_seg_no] = '\n'.join(seg_str_list)
        ram.set_bit(addr, bit_idx, 0)

    p += '\n'.join(jump_seg_str)
    p += f"JMP_SEG_END_{order}:"


for x in range(400):
    for addr in p.rbit():
        ram.set_direct(addr,random.getrandbits(8))
        p += atl.move(atl.D(addr), atl.I(ram.get_direct(addr)))

    creat_jump_link(p, 7, x)
    if x % 16 == 0:
        p += atl.dump()
