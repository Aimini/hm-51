#########################################################
# 2020-01-25 18:07:34
# AI
# ins: ANL C, bit
#########################################################

import random

from .. import testutil as u
from ..sim51util import SIMRAM
from ..asmconst import *

p = u.create_test()
ram = SIMRAM()


def init(addr, p):
    v = random.getrandbits(8)
    p += atl.move(atl.D(addr),atl.I(v))
    ram.set_direct(addr, v)
    

def test(addr, idx, p):
    B = ram.get_bit(addr, idx)
    C = ram.get_bit(SFR_PSW.x, 7)
    ram.set_bit(SFR_PSW.x, 7, C & B)
    p += f"ANL C, {atl.BIT(addr, idx)}"

    p += atl.aste(SFR_PSW, atl.I(ram.get_direct(SFR_PSW.x)))
    

for x in range(27):
    p.iter_direct(init)
    p.iter_bit(test)

