#########################################################
# 2020-01-28 15:25:20
# AI
# ins: MOV Rn, direct
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
    


def test_rn(RN, p):
    value = random.getrandbits(8)
    ris = list(p.rdirect())

    addr = random.choice(ris)
    while addr == SFR_PSW.x:  # don't touch PSW, may cause rs change.
        addr = random.choice(ris)

    p += atl.move(atl.D(addr), atl.I(value))
    p += f'MOV {RN}, {atl.D(addr)}'

    ram.set_direct(addr, value)
    ram.set_iram(RN.addr, ram.get_direct(addr))

    p += atl.aste(atl.D(RN.addr), atl.I(ram.get_iram(RN.addr)))
    


for _ in range(128):
    p.iter_rn(test_rs, test_rn)
