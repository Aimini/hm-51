#########################################################
# 2020-01-27 18:49:23
# AI
# ins: CLR A
#########################################################

import __util as u
import random
from __asmconst import *
from __numutil import numutil as ntl
from __51util import SIMRAM

p = u.create_test()

for x in range(240):
    a = random.getrandbits(8)
    p += f'''
    MOV ACC, {atl.I(a)}
    CLR A
    '''

    p += atl.aste(SFR_A, I_00)
