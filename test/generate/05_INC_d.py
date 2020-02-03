#########################################################
# 2020-01-08 19:45:35
# AI
# ins: INC direct
#########################################################

import __util as u
import random
from __asmconst import *

p = u.create_test()

def one(d, p):
    d = atl.D(d)
    start =random.getrandbits(8)
    p += atl.move(d, atl.I(start))
    for x in range(20):
        p += f'INC {d}'
        p += atl.aste(d, atl.I((x + start + 1)%256))

p.iter_direct_no_psw(one)