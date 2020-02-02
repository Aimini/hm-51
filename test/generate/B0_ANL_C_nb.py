#########################################################
# 2020-01-25 18:19:52
# AI
# ins: ANL C, /bit
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
    ram.set_direct(addr, v)
    

def test(addr, idx, p):
    B = ram.get_bit(addr, idx)
    C = ram.get_bit(SFR_PSW.x, 7)
    ram.set_bit(SFR_PSW.x, 7, C & ~B)
    p += f"ANL C, /{atl.BIT(addr, idx)}"

    p += atl.aste(SFR_PSW, atl.I(ram.get_direct(SFR_PSW.x)))
    

for x in range(29):
    p.iter_is(init)
    p.iter_bit(test)

