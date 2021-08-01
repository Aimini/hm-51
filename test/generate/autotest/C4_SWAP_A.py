#########################################################
# 2020-01-27 18:09:49
# AI
# ins: SWAP A
#########################################################

import random

from .. import testutil as u
from ..asmconst import *

p = u.create_test()

for _ in range(1000):
    A = random.getrandbits(8)
    R = A >> 4 | ((A & 0xF) << 4)
    p += f"MOV ACC, {atl.I(A)}"
    p += f"SWAP A"
    p += atl.aste(SFR_A, atl.I(R))