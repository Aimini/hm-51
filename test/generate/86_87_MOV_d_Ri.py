#########################################################
# 2020-01-28 16:11:33
# AI
# ins: MOV direct, @Ri
#########################################################

import __util as u
import random
from __asmconst import *
from __numutil import numutil as ntl
from __51util import SIMRAM

p = u.create_test()


ram = SIMRAM()
def init_ram(addr, p):
    value = random.getrandbits(8)
    p += atl.move(atl.D(addr),atl.I(value))
    ram[addr] = value
    return ""

def test_rs(rs, psw_rs, p):    
    p += ";; set rs" 
    p += atl.move(SFR_PSW, atl.I(psw_rs))
    ram[SFR_PSW.x] = psw_rs
    return ""

def test_ri(RI, p):
    indirect = random.getrandbits(7)
    value = random.getrandbits(8)

    ris = list(p.ris())
    addr = random.choice(ris)
    
    while addr == SFR_PSW.x: # don't touch PSW, may cause rs change.
        addr = random.choice(ris)

    p += atl.move(atl.D(indirect), atl.I(value))
    p += atl.move(atl.D(RI.addr), atl.I(indirect))
    p += f'MOV {atl.D(addr)}, {RI}'
    
    
    ram[indirect] = value
    ram[RI.addr] = indirect
    ram[addr] = ram[ram[RI.addr]]

    p += atl.aste(atl.D(addr), atl.I(ram[indirect]))
    return ""




for _ in range(64):
    p.iter_is(init_ram)
    p.iter_ri(test_rs, test_ri)
