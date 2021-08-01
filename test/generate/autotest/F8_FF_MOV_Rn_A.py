#########################################################
# 2020-01-28 17:19:17
# AI
# ins: MOV Rn, A
#########################################################

import random

from .. import testutil as u
from ..asmconst import *

p = u.create_test()



def test_rs(rs, psw_rs, p):    
    p += ";; set rs" 
    p += atl.move(SFR_PSW, atl.I(psw_rs))
    

def test_rn(RN, p):
    a = random.getrandbits(8)

    p += atl.move(SFR_A, atl.I(a))
    p += f'MOV {RN}, A'


    p += atl.aste(atl.D(RN.addr), atl.I(a))
    




for x in range(128):
    p.iter_rn(test_rs, test_rn)
