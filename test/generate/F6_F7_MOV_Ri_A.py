#########################################################
# 2020-01-28 13:15:09
# AI
# ins: MOV @Ri, A
#########################################################

import __util as u
import random
from __asmconst import *
from __numutil import numutil as ntl
from __51util import SIMRAM

p = u.create_test()
ram = SIMRAM()



def test_rs(rs, psw_rs, p):    
    p += ";; set rs" 
    p += atl.move(SFR_PSW, atl.I(psw_rs))
    ram[SFR_PSW.x] = psw_rs
    return ""

def test_ri(RI, p):
    indirect = random.getrandbits(7)
    a = random.getrandbits(8)

    p += atl.move(atl.D(RI.addr), atl.I(indirect))
    p += atl.move(SFR_A, atl.I(a))
    p += f'MOV {RI}, A'

    ram[RI.addr] = indirect
    ram[SFR_A.x] = a
    ram[ram[RI.addr]] = ram[SFR_A.x]

    p += atl.aste(atl.D(indirect), atl.I(ram[indirect]))
    return ""




for x in range(256):
    p.iter_ri(test_rs, test_ri)
