#########################################################
# 2020-01-28 18:34:32
# AI
# ins: MOV A, #immed
#########################################################

import random

from .. import testutil as u
from ..asmconst import *
from ..numutil import numutil as ntl

p = u.create_test()
    
def one(value, p):
    p += f'MOV A, {atl.I(value)}'
    p += atl.aste(SFR_A, atl.I(value))
    

for value in ntl.bound(8):
    one(value, p)

for _ in range(4096):
    one(random.getrandbits(8), p)
