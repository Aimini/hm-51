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
    p += "MOV SP, #0xFF"
    ram[SFR_SP.x] = 0xFF
    for _ in range(count):
        while True:
            addr = random.choice(list(p.ris()))
            if addr != SFR_SP.x:
                break

        value = random.getrandbits(8)
        ram[addr] = value
        ram[SFR_SP.x] += 1
        ram[SFR_SP.x] &= 0xFF
        ram[ram[SFR_SP.x]] = ram[addr]
        p += atl.move(atl.D(addr),atl.I(value))
        p += f'PUSH {addr}'


for x in range(100):
    one(p,128)

    
