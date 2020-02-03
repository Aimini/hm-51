#########################################################
# 2020-01-22 22:44:40
# AI
# ins: ANL direct, A
#########################################################

import __util as u
import random
from __asmconst import *
from __numutil import numutil as ntl
from __51util import SIMRAM

p = u.create_test()
ram = SIMRAM()

for x in range(24):
    # load_random_data
    for addr in p.rdirect():
        value = random.getrandbits(8)
        ram.set_direct(addr, value)
        p += atl.move(atl.D(addr), atl.I(value))

    for addr in p.rdirect():
        value = random.getrandbits(8)
        p += f"MOV {SFR_A}, {atl.I(value)}"
        ram.set_direct(SFR_A.x, value)

        p += f"ANL {atl.D(addr)}, A"
        A = ram.get_direct(SFR_A.x)
        v = ram.get_direct(addr)
        ram.set_direct(addr, A & v)

        p += atl.aste(atl.D(addr), atl.I(ram.get_direct(addr)))

