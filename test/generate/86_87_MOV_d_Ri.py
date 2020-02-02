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
    ram.set_direct(addr, value)
    

def test_rs(rs, psw_rs, p):    
    p += ";; set rs" 
    p += atl.move(SFR_PSW, atl.I(psw_rs))
    ram.set_direct(SFR_PSW.x, psw_rs)
    

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
    
    ram.bulid_indirect(RI.addr, indirect, value)
    p += atl.aste(atl.D(addr), atl.I(ram.get_iram(indirect)))
    




for _ in range(64):
    p.iter_is(init_ram)
    p.iter_ri(test_rs, test_ri)
