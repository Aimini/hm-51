#########################################################
# 2020-01-22 09:32:49
# AI
# ins: ADD A, #immed 
#########################################################

import __util as u
import random
from __asmconst import *
from __numutil import numutil as ntl
p = u.create_test()

A = 0
for x in range(256):
    p += "ADD A,{}".format(atl.I(x))
    A += x
    A %= 256
    p += atl.aste(SFR_A, atl.I(A))

for x in ntl.bound(8):
    p += "ADD A,{}".format(atl.I(x))
    A += x
    A %= 256
    p += atl.aste(SFR_A, atl.I(A))
    p += atl.dump()

for x in range(1024):
    i = random.getrandbits(8)
    p += "ADD A,{}".format(atl.I(i))
    A += i
    A %= 256
    p += atl.aste(SFR_A, atl.I(A))