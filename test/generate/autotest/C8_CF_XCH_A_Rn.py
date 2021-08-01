#########################################################
# 2020-01-28 17:43:32
# AI
# ins: XCH A, Rn
#########################################################

import random

from .. import testutil as u
from ..asmconst import *

p = u.create_test()



def test_rs(rs, psw_rs, p):    
    p += ";; set rs" 
    p += atl.move(SFR_PSW, atl.I(psw_rs))
    return ""

def test_rn(RN, p):
    a = random.getrandbits(8)
    value = random.getrandbits(8)
    p += atl.move(SFR_A, atl.I(a))
    p += atl.move(atl.D(RN.addr), atl.I(value))
    p += f'XCH A, {RN}'


    p += atl.aste(SFR_A, atl.I(value))
    p += atl.aste(atl.D(RN.addr), atl.I(a))
    return ""




for x in range(64):
    p.iter_rn(test_rs, test_rn)
