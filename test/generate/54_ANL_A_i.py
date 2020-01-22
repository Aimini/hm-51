#########################################################
# 2020-01-22 13:38:48
# AI
# ins: ADDC A, #immed 
#########################################################

import __util as u
import random
from __asmconst import *
from __numutil import numutil as ntl

p = u.create_test()

p(atl.move(SFR_A, I_FF))
for x in range(8):
    mask = (~(1 << x)) & 0xFF
    p(f"ANL A,{atl.I(mask)}")
    r = (0xFF << (x + 1)) & 0xFF
    p(atl.aste(SFR_A, atl.I(r)))

A = 0
p(atl.move(SFR_A, I_00))
for idx,x in enumerate(ntl.bound(8)):
    p(f"ANL A,{atl.I(x)}")
    A &= x
    p(atl.aste(SFR_A, atl.I(A)))
    p(atl.dump(idx))

for _ in range(4096):
    v1 = random.getrandbits(8)
    v2 = random.getrandbits(8)
    r = atl.I(v1 & v2)

    p(atl.move(SFR_A, atl.I(v1)))
    p(f"ANL A,{r}")
    p(atl.aste(SFR_A, r))