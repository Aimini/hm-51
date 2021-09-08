#########################################################
# 2020-01-28 13:15:09
# AI
# ins: MOV @Ri, A
#########################################################

import random

from .. import testutil as u
from ..sim51util import SIMRAM
from ..asmconst import *

p = u.create_test()
ram = SIMRAM()



def test_rs(rs, psw_rs, p):    
    p += ";; set rs" 
    p += atl.move(SFR_PSW, atl.I(psw_rs))
    ram.set_direct(SFR_PSW.x, psw_rs)
    

def test_ri(RI, p):
    indirect = random.getrandbits(8)
    a = random.getrandbits(8)

    p += atl.move(atl.D(RI.addr), atl.I(indirect))
    p += atl.move(SFR_A, atl.I(a))
    p += f'MOV {RI}, A'

    ram.set_iram(RI.addr, indirect)
    ram.set_direct(SFR_A.x, a)
    ram.set_iram(indirect, ram.get_direct(SFR_A.x))

    p += atl.aste(RI, atl.I(ram.get_iram(ram.get_direct(RI.addr))))
    




for x in range(486):
    p.iter_ri(test_rs, test_ri)
