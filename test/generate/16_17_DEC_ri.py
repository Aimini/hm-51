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
    return atl.move(SFR_PSW, atl.I(psw_rs))

def iter_ri(RI, p):
    t = 100
    while True:
        addr = random.getrandbits(7)
        if addr != RI:
            break
    
    p(atl.move(atl.D(RI.addr), atl.I(addr)))
    start =random.getrandbits(8)

    p(atl.move(atl.D(addr), atl.I(start)))
    for x in range(t):
        p("DEC {}".format(RI))
        p(atl.aste(atl.D(addr), atl.I((start - x - 1)%256)))
    return ""



p.iter_ri(init_rs, iter_ri)