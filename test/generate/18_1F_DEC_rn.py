#########################################################
# 2020-01-22 00:09:24
# AI
# ins: DEC Rn
#########################################################

import __util as u
import random
from __asmconst import *

p = u.create_test()
def init_rs(rs):
    return atl.move(SFR_PSW, atl.I(rs << 3))

def iter_rn(rs,rn):
    t = 100
    rn = atl.RN(rs, rn)
    start =random.getrandbits(8)

    p(atl.move(atl.D(rn.addr), atl.I(start)))
    for x in range(t):
        p("DEC {}".format(rn))
        p(atl.aste(atl.D(rn.addr), atl.I((start - x - 1)%256)))
    return ""



p.iter_rn(init_rs, iter_rn)