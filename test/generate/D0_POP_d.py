#########################################################
# 2020-01-27 21:13:38
# AI
# ins: PUSH direct
#########################################################

import __util as u
import random
from __asmconst import *
from __numutil import numutil as ntl
from __51util import SIMRAM



p = u.create_test()
ram = SIMRAM()

def one(p, count):
    '''
    count:int
        must less than or equal to 128
    '''
    ram[SFR_SP.x] = 0x7F
    p += f'MOV SP, {atl.I(ram[SFR_SP.x])}'
    for x in range(0x80):
        ram[x] = random.getrandbits(8)
        p += atl.move(atl.D(x), atl.I(ram[x]))
        
    for _ in range(count):
        while True:
            addr = random.choice(list(p.ris()))
            if addr != SFR_SP.x:
                break
            
        ram[addr] = ram[ram[SFR_SP.x]]
        ram[SFR_SP.x] -= 1
        ram[SFR_SP.x] &= 0xFF
        
        p += f'POP {atl.D(addr)}'
        p += atl.aste(atl.D(addr),atl.I(ram[addr]))

for x in range(32):
    one(p,128)

    
