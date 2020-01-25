#########################################################
# 2020-01-25 17:39:15
# AI
# ins: ORL C, bit
#########################################################

import __util as u
import random
from __asmconst import *
from __numutil import numutil as ntl
from __51util import SIMRAM

p = u.create_test()
ram = SIMRAM()


def init(addr, p):
    v = random.getrandbits(8)
    p += atl.move(atl.D(addr),atl.I(v))
    ram[addr] = v
    return ""

def test(addr, idx, p):
    ram.set_bit(addr, idx,ram.bit(SFR_PSW.x, 7))
    
    p += f"MOV {atl.BIT(addr, idx)}, C"

    p += atl.aste(SFR_PSW, atl.I(ram[SFR_PSW.x]))
    return ""

for x in range(29):
    p.iter_is(init)
    p.iter_bit(test)

