#########################################################
# 2020-01-27 17:43:23
# AI
# ins: CPL C
#########################################################

import __util as u
from __asmconst import *
import random
p = u.create_test()
for x in range(1000):
    value = random.getrandbits(8)
    p += atl.move(SFR_PSW, atl.I(value))
    p += "CPL C"
    target = (value & 0x7F) | (~value & 0x80)
    p += atl.aste(SFR_PSW,  atl.I(target & 0xFE)) # abandon PF