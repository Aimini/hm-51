#########################################################
# 2020-01-22 22:33:59
# AI
# ins: ORL direct, A
#########################################################

import __util as u
import random
from __asmconst import *
from __numutil import numutil as ntl
from __51util import SIMRAM

p = u.create_test()
ram = SIMRAM()

def init_ram(addr):
    
    p(";; init ram with random data.")
    v = random.getrandbits(8)
    ram[addr] = v
    return atl.move(atl.D(addr),atl.I(v))

def init_rs(rs):
    
    p(";; load random indirect address to ri")
    a = 0
    psw = rs << 3
    p(atl.move(SFR_A, atl.I(a)))
    p(atl.move(SFR_PSW, atl.I(psw)))
    
    ram[SFR_A.x] =  a
    ram[SFR_PSW.x] = psw

    for x in range(2):
        ri_addr = psw + x
        indirect = random.getrandbits(7)
        p(atl.move(atl.D(ri_addr), atl.I(indirect)))
        ram[ri_addr] = indirect
    return ""


def init_ri(rs, ri):
    p(f"ORL A, {atl.RI(rs, ri)}")
    ri_addr = (rs << 3) + ri
    indirect = ram[ri_addr]
    ram[SFR_A.x] |= ram[indirect]

    p(atl.aste(SFR_A, atl.I(ram[SFR_A.x])))
    return ""

for x in range(100):
    p.iter_is(init_ram)
    p.iter_ri(init_rs, init_ri)