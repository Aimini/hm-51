#########################################################
# 2020-01-21 21:49:51
# AI
# ins: DEC A
#########################################################

from .. import testutil as u
from ..asmconst import *

p = u.create_test()


for x in range(256):
    p += 'DEC A'
    p += atl.aste(SFR_A, atl.I((-1-x) % 256))
