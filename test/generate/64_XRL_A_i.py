#########################################################
# 2020-01-22 13:38:48
# AI
# ins: XRL A, #immed 
#########################################################

import __util as u
import random
from __asmconst import *
from __numutil import numutil as ntl

p = u.create_test()

p(atl.move(SFR_A, I_FF))
A = 0xFF
for x in range(8):
    mask = (~(1 << x)) & 0xFF
    
    p(f"XRL A,{atl.I(mask)}")
    A ^= mask
    p(atl.aste(SFR_A, atl.I(A)))




p(atl.move(SFR_A, I_00))
A = 0
for idx,x in enumerate(ntl.bound(8)):
    p(f"XRL A,{atl.I(x)}")
    A ^= x
    p(atl.aste(SFR_A, atl.I(A)))
    p(atl.dump(idx))

for _ in range(4096):
    v1 = random.getrandbits(8)
    v2 = random.getrandbits(8)
    r = atl.I(v1 ^ v2)
    
    p(atl.move(SFR_A, atl.I(v1)))
    p(f"XRL A,{atl.I(v2)}")
    p(atl.aste(SFR_A, r))