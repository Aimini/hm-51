#########################################################
# 2020-01-23 23:25:05
# AI
# ins: CPL A
#########################################################

from .. import testutil as u
from ..asmconst import *

p = u.create_test()

for value in range(0x100):
    p += atl.move(SFR_A, atl.I(value))
    p += "CPL A"
    p += atl.aste(SFR_A, atl.I((~value) & 0xFF))

