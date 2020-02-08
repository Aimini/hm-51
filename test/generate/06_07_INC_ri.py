#########################################################
# 2020-01-08 19:45:35
# AI
# ins: INC @Ri
#########################################################

import __util as u
import random
from __asmconst import *

p = u.create_test()

t = 4


def init_rs(rs, psw_rs, p):
    p += atl.move(SFR_PSW, atl.I(psw_rs))


def iter_ri(RI, p):
    while True:
        indirect = random.getrandbits(8)
        if indirect != RI.addr:
            break

    p += atl.move(atl.D(RI.addr), atl.I(indirect))
    start = random.getrandbits(8)

    p += atl.move(RI, atl.I(start))
    for x in range(t):
        p += f'INC {RI}'
        p += atl.aste(RI, atl.I((start + x + 1) % 256))

for x in range(192):
    p.iter_ri(init_rs, iter_ri)
