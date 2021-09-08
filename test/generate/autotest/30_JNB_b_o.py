#########################################################
# 2020-01-25 19:40:04
# AI
# ins: JNB bit, offset
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

jump_limit =f'''
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
'''
p += jump_limit
p += atl.clear_iram()
p += atl.clear_reg()


for addr in p.rbit():
    ram.set_direct(addr,random.getrandbits(8))
    p += atl.move(atl.D(addr), atl.I(ram.get_direct(addr)))

def random_bit(x):
    yield random.choice(list(p.rbit()))
    
valueiter = itertools.chain(p.rbit(), itertools.cycle(random_bit(8)))

def creat_one_test_seg(order, seg_no, target, addr, bit_idx, value):
    seg_str_list = []

    seg_str_list.append(f'JMP_SEG_{order}_{seg_no}:')
    seg_str_list.append(atl.move(atl.D(addr),atl.I(value)))
    ram.set_direct(addr, value)

    bit_addr =atl.BIT(addr, bit_idx)


    if ram.get_bit(addr, bit_idx) == 0:
        seg_str_list.append(f'JNB {bit_addr}, {target}')
        seg_str_list.append(atl.crash())
    else:
        wrong_seg = f'SEG_WRONG_{order}_{seg_no}'
        seg_str_list.append(f'JNB {bit_addr}, {wrong_seg}')
        seg_str_list.append(f'SJMP {target}')
        seg_str_list.append(f'{wrong_seg}:')
        seg_str_list.append(atl.crash())
    
    return '\n'.join(seg_str_list)

def creat_jump_link( jump_count, order):
    jmpords = list(range(jump_count))
    random.shuffle(jmpords)
    start = jmpords[0]

    all_seg_str_list = list(range(jump_count))
    for idx, seg_no in enumerate(jmpords):
        
        value = random.getrandbits(8)
        bit_idx = random.getrandbits(3)
        addr = next(valueiter)
        
        if idx < len(jmpords) - 1:
            next_seg_no = jmpords[idx + 1]
            target = f'JMP_SEG_{order}_{next_seg_no}'
        else:
            target = f'JMP_SEG_END_{order}'
        
        r = creat_one_test_seg(order, seg_no, target, addr, bit_idx, value)
        all_seg_str_list[seg_no] = r

    all_seg_str_list.insert(0,f'SJMP JMP_SEG_{order}_{start}')
    all_seg_str_list.append(f'JMP_SEG_END_{order}:')
    return '\n'.join(all_seg_str_list) 

for x in range(886):
    p += creat_jump_link(7, x)

