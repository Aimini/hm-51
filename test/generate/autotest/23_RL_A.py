#########################################################
# 2020-01-21 20:50:01
# AI
# ins: RL A
#########################################################

import random

from .. import testutil as u
from ..asmconst import *

p = u.create_test()


for x in range(4900):
    value = random.getrandbits(8)
    r = ((value >> 7) & 1) | ((value & 0x7F) << 1)
    p += atl.move(SFR_A, atl.I(value))
    p += 'RL A'
    p += atl.aste(SFR_A, atl.I(r))
