#########################################################
# 2020-01-08 19:45:35
# AI
# ins: MOV direct, #immed.
# how: write address of the iram and SFR into itself.
#########################################################

from .. import testutil as u
from ..asmconst import *

p = u.create_test()

def one(addr, p):
    # set memory cells' value to it's address
    p += atl.move(atl.D(addr),atl.I(addr))


p.iter_direct(one)
