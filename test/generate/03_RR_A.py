#########################################################
# 2020-01-08 19:45:35
# AI
# ins: RR A
#########################################################

import __util as u
import random
from __asmconst import *

p = u.create_test()

for x in range(4900):
    value = random.getrandbits(8)
    r = ((value & 1) << 7) | (value >> 1)

    p += f"MOV ACC, #{hex(value)}"
    p += f"RR A"
    p += atl.aste(SFR_A, atl.I(r))