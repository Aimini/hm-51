#########################################################
# 2020-01-22 22:58:47
# AI
# ins: AND direct, A
#########################################################

import __util as u
import random
from __asmconst import *
from __numutil import numutil as ntl
from __51util import SIMRAM

p = u.create_test()
ram = SIMRAM()

for x in range(32):
    # load_random_data
    for addr in p.ris():
        value = random.getrandbits(8)
        ram[addr] = value
        p += atl.move(atl.D(addr), atl.I(value))

    for addr in p.ris():
        p += f"ANL A, {atl.D(addr)}"
        ram[SFR_A.x] &= ram[addr]

        p += atl.aste(SFR_A, atl.I(ram[SFR_A.x]))