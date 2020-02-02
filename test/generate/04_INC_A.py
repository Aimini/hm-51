#########################################################
# 2020-01-08 19:45:35
# AI
# ins: INC A
#########################################################

import __util as u
import random
from __asmconst import *

p = u.create_test()


for x in range(256):
    p += 'INC A'
    p += atl.aste(SFR_A, atl.I((x + 1)%256))
    
