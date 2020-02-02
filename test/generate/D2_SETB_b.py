#########################################################
# 2020-01-25 16:20:20
# AI
# ins: SETB bit
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
    ram.set_bit(addr,idx,1)
    p += f"SETB {atl.BIT(addr, idx)}"

    p += atl.aste(atl.D(addr), atl.I(ram.get_direct(addr)))
    

for x in range(29):
    p.iter_is(init)
    p.iter_bit(test)

