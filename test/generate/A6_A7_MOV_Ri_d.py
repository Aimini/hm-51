#########################################################
# 2020-01-28 15:25:20
# AI
# ins: MOV @Ri, direct
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
    ris = list(p.ris())
    addr = random.choice(ris)
    while addr == SFR_PSW.x: # don't touch PSW, may cause rs change.
        addr = random.choice(ris)
    value = random.getrandbits(8)

    p += atl.move(atl.D(addr), atl.I(value))
    p += atl.move(atl.D(RI.addr), atl.I(indirect))
    p += f'MOV {RI}, {atl.D(addr)}'
    
    ram[addr] = value
    ram[RI.addr] = indirect
    ram[ram[RI.addr]] = ram[addr]

    p += atl.aste(atl.D(indirect), atl.I(ram[indirect]))
    return ""




for _ in range(256):
    p.iter_ri(test_rs, test_ri)
