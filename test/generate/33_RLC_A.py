#########################################################
# 2020-01-21 20:55:32
# AI
# ins: RLC A
#########################################################

import __util as u
import random
from __asmconst import *

p = u.create_test()

CY = 0
for x in range(3000):
    value = random.getrandbits(8)
    rv = CY | ((value << 1) & 0xFE)
    CY = (value >> 7) & 1

    p(atl.move(SFR_A, atl.I(value)))
    p("RLC A")
    p(atl.aste(SFR_A, atl.I(rv)))
    if x % 50 == 0:
        p(atl.dump())
