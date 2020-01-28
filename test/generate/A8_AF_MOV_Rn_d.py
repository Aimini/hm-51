#########################################################
# 2020-01-28 15:25:20
# AI
# ins: MOV Rn, direct
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


def test_rn(RN, p):
    value = random.getrandbits(8)

    ris = list(p.ris())
    addr = random.choice(ris)
    while addr == SFR_PSW.x:  # don't touch PSW, may cause rs change.
        addr = random.choice(ris)

    p += atl.move(atl.D(addr), atl.I(value))
    p += f'MOV {RN}, {atl.D(addr)}'

    ram[addr] = value
    ram[RN.addr] = ram[addr]

    p += atl.aste(atl.D(RN.addr), atl.I(ram[RN.addr]))
    return ""


for _ in range(128):
    p.iter_rn(test_rs, test_rn)
