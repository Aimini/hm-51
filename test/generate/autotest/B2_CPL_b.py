#########################################################
# 2020-01-25 16:54:33
# AI
# ins: CPL bit
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
    ram.set_bit(addr,idx, ~ram.get_bit(addr,idx))
    p += f"CPL {atl.BIT(addr, idx)}"

    p += atl.aste(atl.D(addr), atl.I(ram.get_direct(addr)))
    
for x in range(27):
    p.iter_direct(init)
    p.iter_bit(test)

