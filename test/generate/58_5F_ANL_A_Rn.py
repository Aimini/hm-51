#########################################################
# 2020-01-23 16:03:11
# AI
# ins: ORL A, @Rn
#########################################################

import __util as u
import random
from __asmconst import *
from __numutil import numutil as ntl
from __51util import SIMRAM

p = u.create_test()
ram = SIMRAM()

op_name = "ANL"


def op(a, b): return a & b



def init_rs(rs, psw_rs, p):
    p += f";;  set register bank{rs} in psw" 

    p += atl.move(SFR_PSW, atl.I(psw_rs))
    ram[SFR_PSW.x] = psw_rs

    return ""


def init_rn(RN, p):
    p += f";;  load random value into {RN}" 

    value = random.getrandbits(8)

    p += atl.move(atl.D(RN.addr), atl.I(value))
    ram[RN.addr] = value

    return ""


def test_rs(rs, psw_rs, p):    
    a = 0x00
    p += atl.move(SFR_PSW, atl.I(psw_rs))
    p += atl.move(SFR_A, atl.I(a))

    ram[SFR_PSW.x] = psw_rs
    ram[SFR_A.x] = a
    return ""

def test_rn(RN, p):
    p += f"{op_name} A, {RN}"
    ram[SFR_A.x] = op(ram[SFR_A.x], ram[RN.addr])

    p += atl.aste(SFR_A, atl.I(ram[SFR_A.x]))
    return ""


def test_bound(RN, p):
    A = random.getrandbits(8)
    p += atl.move(SFR_A, atl.I(A))
    ram[SFR_A.x] = A
    for value in ntl.bound(8):
        p += atl.move(atl.D(RN.addr),  atl.I(value))
        p += f"{op_name} A, {RN}"

        ram[SFR_A.x] = op(ram[SFR_A.x], ram[RN.addr])
        ram[RN.addr] = value
    return ""


for x in range(128):
    p.iter_rn(init_rs, init_rn)
    p.iter_rn(test_rs, test_rn)

p.iter_rn(lambda a,b: "", test_bound)
