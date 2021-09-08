#########################################################
# 2020-01-08 19:45:35
# AI
# ins: INC A
#########################################################

from .. import testutil as u
from ..asmconst import *

p = u.create_test()


for x in range(256):
    p += 'INC A'
    p += atl.aste(SFR_A, atl.I((x + 1)%256))
    
