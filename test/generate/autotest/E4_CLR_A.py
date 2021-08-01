#########################################################
# 2020-01-27 18:49:23
# AI
# ins: CLR A
#########################################################

import random

from .. import testutil as u
from ..asmconst import *

p = u.create_test()

for x in range(240):
    a = random.getrandbits(8)
    p += f'''
    MOV ACC, {atl.I(a)}
    CLR A
    '''

    p += atl.aste(SFR_A, I_00)
