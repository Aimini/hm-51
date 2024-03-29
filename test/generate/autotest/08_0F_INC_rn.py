#########################################################
# 2020-01-08 19:45:35
# AI
# ins: INC Rn
#########################################################

import random

from .. import testutil as u
from ..asmconst import *

p = u.create_test()


def init_rs(rs, psw_rs, p):
    p += atl.move(SFR_PSW, atl.I(psw_rs))


def init_rn(RN, p):
    t = 100
    start = random.getrandbits(8)

    p += atl.move(atl.D(RN.addr), atl.I(start))
    for x in range(t):
        p += f"INC {RN}"
        p += atl.aste(atl.D(RN.addr), atl.I((start + x + 1) % 256))


p.iter_rn(init_rs, init_rn)
