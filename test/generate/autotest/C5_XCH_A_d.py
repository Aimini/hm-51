#########################################################
# 2020-01-28 12:24:37
# AI
# ins: XCH A, direct
#########################################################

import random

from .. import testutil as u
from ..sim51util import SIMRAM
from ..asmconst import *

p = u.create_test()
ram = SIMRAM()


def fill_one(addr, p):
    a = random.getrandbits(8)
    value = random.getrandbits(8)
    p += f'''
    MOV ACC, {atl.I(a)}
    MOV {atl.D(addr)}, {atl.I(value)}
    XCH A, {atl.D(addr)}
    '''
    ram.set_direct(SFR_A.x, a)
    ram.set_direct(addr,  value)
    # swap
    temp = ram.get_direct(SFR_A.x)
    ram.set_direct(SFR_A.x,  ram.get_direct(addr))
    ram.set_direct(addr, temp)

    p += atl.aste(SFR_A, atl.I(ram.get_direct(SFR_A.x)))
    p += atl.aste(addr,  atl.I(ram.get_direct(addr)))


for _ in range(16):
    p.iter_direct(fill_one)
