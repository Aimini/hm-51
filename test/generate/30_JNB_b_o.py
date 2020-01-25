#########################################################
# 2020-01-25 19:40:04
# AI
# ins: JNB bit, offset
#########################################################

import __util as u
import random
import itertools
from __asmconst import *
from __numutil import numutil as ntl
from __51util import SIMRAM
p = u.create_test()
ram = SIMRAM()

jump_limit =f"""
; PC = 0
MOV 0xE0, #0      ; SET A TO 0x80
JNB 0xE0.0, JMP_LIMIT_127 ; JUMP TO  2 + 0x7F = 0x81
; PC = 2
NOP
; PC = 3
JMP_LIMIT_256:
JNB 0xE0.0, JMP_SEG_START


CSEG AT 0x81
JMP_LIMIT_127:
JNB 0xE0.0,JMP_LIMIT_256 ; JUMP TO 0x83 - 0x80 = 0x03
; PC = 0x83

JMP_SEG_START:
"""
p += jump_limit

for addr in p.rbit():
    ram[addr] = random.getrandbits(8)
    p += atl.move(atl.D(addr), atl.I(ram[addr]))

def random_bit(x):
    yield random.choice(list(p.rbit()))
    
valueiter = itertools.chain(p.rbit(), itertools.cycle(random_bit(8)))

def creat_jump_link(p, jump_count, order):
    jmpords = ntl.jl(jump_count)
    start =random.choice(jmpords)
    p += f"""
    SJMP JMP_SEG_{order}_{start}
    """
    
    for idx,next_idx in enumerate(jmpords):
        p += f"JMP_SEG_{order}_{idx}:"
        
        value = random.getrandbits(8)
        bit_idx = random.getrandbits(3)
        addr = next(valueiter)
        
        p += atl.move(atl.D(addr),atl.I(value))
        ram[addr] = value

        bit_addr =atl.BIT(addr, bit_idx)

        if next_idx == start:
            target = f"JMP_SEG_END_{order}"
        else:
            target = f"JMP_SEG_{order}_{next_idx}"

        if ram.bit(addr, bit_idx) == 0:
            p += f"JNB {bit_addr}, {target}"
            p += atl.astl(I_00, I_00)
        else:
            jump_wrong = f"SEG_WRONG_{order}_{idx}"

            p += f"JNB {bit_addr}, {jump_wrong}"
            p += f"SJMP {target}"
            p += f"{jump_wrong}:"
            p += atl.astl(I_00, I_00)

    p += f"JMP_SEG_END_{order}:"

for x in range(500):
    creat_jump_link(p, 7,x)

