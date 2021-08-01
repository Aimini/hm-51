#########################################################
# 2020-01-08 19:45:35
# AI
# ins: MOV direct, #immed.
# how: write address of the iram and SFR into itself.
#########################################################

import random

from .. import testutil as u
from ..asmconst import *

p = u.create_test()

def one(d, p):
    t = 20
    start =random.getrandbits(8)

    p += atl.move(d, atl.I(start))
    for x in range(t):
        p += "DEC {}".format(d)
        if x == SFR_PSW:
            p += atl.aste(d, atl.I((start - (x - 1))%256))
            p += atl.aste(d, atl.I((start - 2*(x + 1))%256))
    

p.iter_direct(one)