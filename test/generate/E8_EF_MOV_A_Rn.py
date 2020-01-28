#########################################################
# 2020-01-28 17:25:15
# AI
# ins: MOV A, Rn
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
    p += atl.move(atl.D(RN.addr), atl.I(value))
    p += f'MOV A, {RN}'


    p += atl.aste(SFR_A, atl.I(value))
    return ""




for x in range(128):
    p.iter_rn(test_rs, test_rn)
