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
    p += "MOV SP, #0xFF"
    ram.set_direct(SFR_SP.x, 0xFF)
    for _ in range(count):
        while True:
            addr = random.choice(list(p.rdirect()))
            if addr != SFR_SP.x:
                break

        value = random.getrandbits(8)
        ram.set_direct(addr, value)
        SP = ram.get_direct(SFR_SP.x)
        SP = (SP + 1) & 0xFF
        ram.set_direct(SFR_SP.x, SP)
        ram.set_iram(SP, ram.get_direct(addr))
        p += atl.move(atl.D(addr),atl.I(value))
        p += f'PUSH {addr}'


for x in range(99):
    one(p,128)

    
