#########################################################
# 2020-01-28 18:26:59
# AI
# ins: MOV Rn, #immed
#########################################################

import random

from .. import testutil as u
from ..asmconst import *

p = u.create_test()

def test_rs(rs, psw_rs, p):
    p += ";; set rs" 
    p += atl.move(SFR_PSW, atl.I(psw_rs))
    

def test_rn(RN, p):
    value = random.getrandbits(8)
    p += f'MOV {RN}, {atl.I(value)}'
    p += atl.aste(atl.D(RN.addr), atl.I(value))
    




for _ in range(128):
    p.iter_rn(test_rs, test_rn)
