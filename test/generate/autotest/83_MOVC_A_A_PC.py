#########################################################
# 2020-01-27 16:00:15
# AI
# ins: MOVC A, @A+PC
#########################################################

import random

from .. import testutil as u
from ..asmconst import *

p = u.create_test()


def one(seg_no):
    s = ''
    value = random.getrandbits(8)
    nop_fill = random.randint(0, 0xFF - 3)
    
    s += f'''
    
    MOV ACC, {atl.I(nop_fill + 3)} ; filled NOP, and MOVC A,@A+PC instructin len.
    MOVC A, @A+PC
    LJMP SEG_ASTE_{seg_no}
    '''

    for _ in range(nop_fill):
        s += 'NOP\n'

    s +=  f'''
    DB {hex(value)}
    SEG_ASTE_{seg_no}:
    {atl.aste(SFR_A, atl.I(value))}
    '''
    return s, 7 + nop_fill + 1 + 3*3


    
        
        

total_len = 0x20 + 1280 # reserve for clear reg and clear iram code
p.is_prepend_clear_reg = False
i = 0
while True:
    s, l = one(i)
    total_len += l
    if total_len < 0x10000:
        p += s
    else:
        break
    i += 1
p += atl.clear_reg()