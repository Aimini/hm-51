#########################################################
# 2020-01-08 19:45:35
# AI
# ins: INC @Ri
#########################################################

import __util as u
import random
from __asmconst import *

p = u.create_test()

t = 100
def init_rs(rs, psw_rs, p):
    p += atl.move(SFR_PSW, atl.I(psw_rs))


def iter_ri(RI, p):
    while True:
        addr = random.getrandbits(7)
        if addr != RI.addr:
            break

    p += atl.move(atl.D(RI.addr), atl.I(addr))
    start = random.getrandbits(8)

    p += atl.move(atl.D(addr), atl.I(start))
    for x in range(t):
        p += f'INC {RI}'
        p += atl.aste(atl.D(addr), atl.I((start + x + 1) % 256))


p.iter_ri(init_rs, iter_ri)
