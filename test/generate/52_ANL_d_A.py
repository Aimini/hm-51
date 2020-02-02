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
    for addr in p.ris():
        value = random.getrandbits(8)
        ram[addr] = value
        p += atl.move(atl.D(addr), atl.I(value))

    for addr in p.ris():
        value = random.getrandbits(8)
        p += f"MOV {SFR_A}, {atl.I(value)}"
        p += f"ANL {atl.D(addr)}, A"
        ram[SFR_A.x] = value
        ram[addr] &= ram[SFR_A.x]
        p += atl.aste(atl.D(addr), atl.I(ram[addr]))

