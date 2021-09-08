#########################################################
# 2020-01-27 17:57:36
# AI
# ins: CLR C
#########################################################

import random

from .. import testutil as u
from ..asmconst import *

p = u.create_test()
for x in range(1000):
    value = random.getrandbits(8)
    p += atl.move(SFR_PSW, atl.I(value))
    p += "CLR C"
    target = value & 0x7E # abandon PF
    p += atl.aste(SFR_PSW,  atl.I(target)) 