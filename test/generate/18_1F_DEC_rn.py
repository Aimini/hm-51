#########################################################
# 2020-01-22 00:09:24
# AI
# ins: DEC RN
#########################################################

import __util as u
import random
from __asmconst import *

p = u.create_test()
def init_rs(rs, psw_rs, p):
    return atl.move(SFR_PSW, atl.I(psw_rs))

def iter_rn(RN, p):
    t = 100
    start =random.getrandbits(8)

    p(atl.move(atl.D(RN.addr), atl.I(start)))
    for x in range(t):
        p("DEC {}".format(RN))
        p(atl.aste(atl.D(RN.addr), atl.I((start - x - 1)%256)))
    return ""



p.iter_rn(init_rs, iter_rn)