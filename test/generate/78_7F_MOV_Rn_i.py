#########################################################
# 2020-01-28 18:26:59
# AI
# ins: MOV Rn, #immed
#########################################################

import __util as u
import random
from __asmconst import *
from __numutil import numutil as ntl

p = u.create_test()

def test_rs(rs, psw_rs, p):
    p += ";; set rs" 
    p += atl.move(SFR_PSW, atl.I(psw_rs))
    return ""

def test_rn(RN, p):
    value = random.getrandbits(8)
    p += f'MOV {RN}, {atl.I(value)}'
    p += atl.aste(atl.D(RN.addr), atl.I(value))
    return ""




for _ in range(128):
    p.iter_rn(test_rs, test_rn)
