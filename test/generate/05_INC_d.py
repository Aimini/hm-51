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

def one(d):
    d = atl.D(d)
    start =random.getrandbits(8)
    p(atl.move(d, atl.I(start)))
    for x in range(20):
        p("INC {}".format(d))
        p(atl.aste(d, atl.I((x + start + 1)%256)))
    return ""

p.iter_is_no_psw(one)