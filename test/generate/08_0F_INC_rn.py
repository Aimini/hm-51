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
def init_rs(rs, psw_rs, p):
    p += atl.move(SFR_PSW, atl.I(psw_rs))
    return ""

def init_rn(RN, p):
    t = 100
    start =random.getrandbits(8)

    p += atl.move(atl.D(RN.addr), atl.I(start))
    for x in range(t):
        p += "INC {}".format(RN)
        p += atl.aste(atl.D(RN.addr), atl.I((start + x + 1)%256))
    return ""



p.iter_rn(init_rs, init_rn)