#########################################################
# 2020-01-27 17:59:38
# AI
# ins: SETB C
#########################################################

import random

from .. import testutil as u
from ..asmconst import *

p = u.create_test()
for x in range(1000):
    value = random.getrandbits(8)
    p += atl.move(SFR_PSW, atl.I(value))
    p += "SETB C"
    target = value | 0x80  # abandon PF
    p += atl.aste(SFR_PSW,  atl.I(target & 0xFE))
