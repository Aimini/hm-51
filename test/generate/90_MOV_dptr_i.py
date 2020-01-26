#########################################################
# 2020-01-26 15:25:57
# AI
# ins: MOV DPTR, #immed
#########################################################

import __util as u
import random
import itertools
from __asmconst import *
from __numutil import numutil as ntl
from __51util import SIMRAM

p = u.create_test()

def test_one(v,p):
    p += f'''
    MOV DPTR, {atl.I(x)}
    {atl.aste(SFR_DPL, atl.I(x & 0xFF))}
    {atl.aste(SFR_DPH, atl.I(x >> 8))}
    '''


for x in ntl.bound(16):
    test_one(x, p)

for _ in range(3100):
    test_one(random.getrandbits(16), p)
