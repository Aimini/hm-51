#########################################################
# 2020-01-28 18:34:32
# AI
# ins: MOV A, #immed
#########################################################

import __util as u
import random
from __asmconst import *
from __numutil import numutil as ntl

p = u.create_test()
    
def one(value, p):
    p += f'MOV A, {atl.I(value)}'
    p += atl.aste(SFR_A, atl.I(value))
    

for value in ntl.bound(8):
    one(value, p)

for _ in range(4096):
    one(random.getrandbits(8), p)
