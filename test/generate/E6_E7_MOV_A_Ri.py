#########################################################
# 2020-01-28 14:01:44
# AI
# ins: MOV A, @Ri
#########################################################

import __util as u
import random
from __asmconst import *
from __numutil import numutil as ntl
from __51util import SIMRAM

p = u.create_test()
ram = SIMRAM()

def init_ram(addr,p):
    
    p += ";; init ram with random data."
    v = random.getrandbits(8)
    ram[addr] = v
    return atl.move(atl.D(addr),atl.I(v))

def init_rs(rs,psw_rs,p):
    return ""


def init_ri(RI, p):
    p += ";; load random indirect address to ri"
    
    indirect = random.getrandbits(7)

    p += atl.move(atl.D(RI.adr),atl.I(indirect))
    ram[RI.addr] = indirect
    return ""

def test_rs(rs,psw_rs,p):
    p += atl.move(SFR_PSW, atl.I(psw_rs))
    ram[SFR_PSW.x] = psw_rs

    return ""


def test_ri(RI, p):
    p += f"MOV A, {RI}"
    ram[SFR_A.x] = ram[ram[RI.addr]]
    p += atl.aste(SFR_A, atl.I(ram[ram[RI.addr]]))
    return ""


for x in range(100):
    p.iter_is(init_ram)
    p.iter_ri(init_rs, init_ri)
