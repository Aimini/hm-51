#########################################################
# 2020-01-26 15:25:57
# AI
# ins: MOV DPTR, #immed
#########################################################

import random

from .. import testutil as u
from ..asmconst import *
from ..numutil import numutil as ntl

p = u.create_test()

def test_one(v,p):
    p += f'''
    MOV DPTR, {atl.I(x)}
    {atl.aste(SFR_DPL, atl.I(x & 0xFF))}
    {atl.aste(SFR_DPH, atl.I(x >> 8))}
    '''


for x in ntl.bound(16):
    test_one(x, p)

for _ in range(3000):
    test_one(random.getrandbits(16), p)
