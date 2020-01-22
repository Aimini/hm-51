#########################################################
# 2020-01-22 22:03:24
# AI
# ins: ANL A, #immed
#########################################################

import __util as u
import random
from __asmconst import *
from __numutil import numutil as ntl
from __51util import SIMRAM

p = u.create_test()
ram = SIMRAM()

# load_random_data
for addr in p.ris():
    value = random.getrandbits(8)
    ram[addr] = value
    p(atl.move(atl.D(addr), atl.I(value)))


for x in range(32):
    for addr in p.ris():
        value = random.getrandbits(8)
        p(f"ANL {atl.D(addr)}, {atl.I(value)}")
        ram[addr] &= value
        p(atl.aste(atl.D(addr), atl.I(ram[addr])))