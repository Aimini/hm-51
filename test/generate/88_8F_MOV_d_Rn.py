#########################################################
# 2020-01-28 18:15:32
# AI
# ins: MOV  direct, Rn
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
    


def test_rn(RN, p):
    value = random.getrandbits(8)

    ris = list(p.ris())
    addr = random.choice(ris)
    while addr == SFR_PSW.x:  # don't touch PSW, may cause rs change.
        addr = random.choice(ris)

    p += atl.move(atl.D(RN.addr), atl.I(value))
    p += f'MOV {atl.D(addr)},{RN}'

    ram[RN.addr] = value
    ram[addr] = ram[RN.addr]

    p += atl.aste(atl.D(addr), atl.I(ram[addr]))
    


for _ in range(128):
    p.iter_rn(test_rs, test_rn)
