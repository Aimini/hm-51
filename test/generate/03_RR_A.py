#########################################################
# 2020-01-08 19:45:35
# AI
# ins: MOV direct, #immed.
# how: write address of the iram and SFR into itself.
#########################################################

import __util as u
import random
from __asmconst import *

p = u.create_test()


for x in range(5000):
    value = random.getrandbits(8)
    p(atl.move(SFR_A, atl.I(value)))
    p("RR A")
    p(atl.aste(SFR_A, atl.I(((value & 1) << 7) | (value >> 1))))
