#########################################################
# 2020-01-28 16:42:04
# AI
# ins: MOV @Ri, #immed
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

def test_ri(RI, p):
    indirect = random.getrandbits(7)
    value = random.getrandbits(8)

    p += atl.move(atl.D(RI.addr), atl.I(indirect))
    p += f'MOV {RI}, {atl.I(value)}'

    p += atl.aste(atl.D(indirect), atl.I(value))
    return ""




for _ in range(256):
    p.iter_ri(test_rs, test_ri)
