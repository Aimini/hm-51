#########################################################
# 2020-01-27 21:13:38
# AI
# ins: PUSH direct
#########################################################

import random

from .. import testutil as u
from ..sim51util import SIMRAM
from ..asmconst import *

p = u.create_test()
ram = SIMRAM()

def one(p, count):
    '''
    count:int
        must less than or equal to 128
    '''
    ram.set_direct(SFR_SP.x, 0x7F)
    p += f'MOV SP, {atl.I(ram.get_direct(SFR_SP.x))}'

    for x in range(0x80):
        ram.set_direct(x, random.getrandbits(8))
        p += atl.move(atl.D(x), atl.I(ram.get_direct(x)))
        
    for _ in range(count):
        while True:
            addr = random.choice(list(p.rdirect()))
            if addr != SFR_SP.x:
                break
        SP =  ram.get_direct(SFR_SP.x)
        ram.set_direct(addr, ram.get_iram(SP))
        ram.set_direct(SFR_SP.x, (SP - 1) & 0xFF)
        
        p += f'POP {atl.D(addr)}'
        p += atl.aste(atl.D(addr),atl.I(ram.get_direct(addr)))

for x in range(32):
    one(p,128)

    
