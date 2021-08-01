#########################################################
# 2020-01-27 17:27:45
# AI
# ins: INC DPTR
#########################################################

import random

from .. import testutil as u
from ..asmconst import *

p = u.create_test()


def one(start, count, p):
    p += f'MOV DPTR, {atl.I(start)}'
    for i in range(count):
        p += 'INC DPTR'

        value = (start + i + 1) & 0xFFFF
        DPH = value >> 8
        DPL = value & 0xFF
        p += atl.aste(SFR_DPL, atl.I(DPL))
        p += atl.aste(SFR_DPH, atl.I(DPH))
    

for x in range(10):
    one(random.getrandbits(16), 320, p)