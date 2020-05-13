#########################################################
# 2020-01-28 16:42:04
# AI
# ins: MOV @Ri, #immed
#
# this is manual test file!
# it's copy the address to IRAM cell itself
#########################################################

import __util as u
import random
from __asmconst import *
from __numutil import numutil as ntl

p = u.create_test()
p.is_prepend_clear_reg = False
p.is_append_dump = False

ri = 0
rs = 0

for i in range(0x20, 256):
    ri = ri + 1
    if ri == 2:
        rs = rs + 1
    rs %= 4
    ri %= 2
    RI = atl.RI(rs, ri)
    p += f'MOV PSW, {atl.I(rs << 3)}'
    p += f'MOV {atl.D(RI.addr)}, {atl.I(i)}'
    p += f'MOV {RI}, {atl.I(i)}'

p += 'MOV PSW, #0'
for i in reversed(range(0x20)):
    p += f'''
        MOV 0x00, {atl.I(i)}
        MOV @R0,  {atl.I(i)}'''