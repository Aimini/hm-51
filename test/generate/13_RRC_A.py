#########################################################
# 2020-01-21 20:33:19
# AI
# ins: RRC A
#########################################################

import __util as u
import random
from __asmconst import *

p = u.create_test()

CY = 0
for x in range(3000):
    value = random.getrandbits(8)
    rv = (CY << 7) | (value >> 1)
    CY = value & 1

    p += atl.move(SFR_A, atl.I(value))
    p += "RRC A"
    p += atl.aste(SFR_A, atl.I(rv))
    if x % 50 == 0:
        p += atl.dump()
