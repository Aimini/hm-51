#########################################################
# 2020-01-08 19:45:35
# AI
# ins: MOV direct, #immed.
# how: write address of the iram and SFR into itself.
#########################################################

import __util as u
from __asmconst import *

p = u.create_test()

def one(*vargs):
    addr = vargs[0]
    # set memory cells' value to it's address
    return atl.move(atl.D(addr),atl.I(addr))


p.iter_is(one)
