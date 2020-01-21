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
A = 0
def one(d):
    t = 20
    start =random.getrandbits(8)

    p(atl.move(d, atl.I(start)))
    for x in range(t):
        p("DEC {}".format(d))
        if x == SFR_PSW:
            p(atl.aste(d, atl.I((start - (x - 1))%256)))
            p(atl.aste(d, atl.I((start - 2*(x + 1))%256)))
    return ""

p.iter_is(one)