#########################################################
# 2020-01-23 17:59:08
# AI
# ins: SUBB A, #immed 
#########################################################

import __util as u
import random
from __asmconst import *
from __numutil import numutil as ntl

p = u.create_test()


A = 0
CY = 0
class do_s_op():
    def __init__(self):
        self.A = 0
        self.CY = 0
    def __call__(self, x):
        self.A = self.A - x - self.CY
        if self.A < 0:
            self.A &= 0xFF
            self.CY = 1
        else:
            self.CY = 0

d = do_s_op()
operation = "SUBB"

for x in range(256):
    p += "{} A,{}".format(operation, atl.I(x))
    d(x)
    p += atl.aste(SFR_A, atl.I(d.A))


for idx,x in enumerate(ntl.bound(8)):
    p += "{} A,{}".format(operation, atl.I(x))
    d(x)
    p += atl.aste(SFR_A, atl.I(d.A))
    p += atl.dump(idx)

for _ in range(1024):
    i = random.getrandbits(8)
    p += "{} A,{}".format(operation, atl.I(i))
    d(i)
    p += atl.aste(SFR_A, atl.I(d.A))