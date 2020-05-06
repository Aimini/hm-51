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


def init_rs(rs, psw_rs, p):
    p += ";;init: set rs"
    p += atl.move(SFR_PSW, atl.I(psw_rs))
    ram.set_direct(SFR_PSW.x, psw_rs)


def init_ri(RI, p):
    p += ";;init: load random immed to random IRAM"
    indirect = random.getrandbits(8)
    value = random.getrandbits(8)

    p += atl.move(atl.D(RI.addr), atl.I(indirect))
    p += atl.move(RI, atl.I(value))
    
    ram.set_iram(RI.addr, indirect)
    ram.set_iram(indirect, value)


def test_rs(rs, psw_rs, p):
    p += ";; set rs"
    p += atl.move(SFR_PSW, atl.I(psw_rs))
    ram.set_direct(SFR_PSW.x, psw_rs)


def test_ri(RI, p):
    indirect = random.getrandbits(8)
    value = random.getrandbits(8)

    ris = list(p.rdirect())
    addr = random.choice(ris)
    while addr == SFR_PSW.x:  # don't touch PSW, may cause rs change.
        addr = random.choice(ris)

    p += f'MOV {atl.D(addr)}, {RI}'

    indirect = ram.get_iram(RI.addr)
    value = ram.get_iram(indirect)
    ram.set_direct(addr, value)
    p += atl.aste(atl.D(addr), atl.I(value))


for _ in range(64):
    p.iter_ri(init_rs, init_ri)
    p.iter_ri(test_rs, test_ri)
