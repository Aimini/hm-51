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

op_name = "ADDC"


def do(B):
    cy = (ram[SFR_PSW.x] & 0x80) >> 7
    A = ram[SFR_A.x]
    SL = (A&0xF) + (B&0xF) + cy
    S  =  A  + B + cy

    if S > 0xFF:
        ram[SFR_PSW.x] |= 0x80
    else:
        ram[SFR_PSW.x] &= 0x7F
    
    if SL > 0xF:
        ram[SFR_PSW.x] |= 0x40
    else:
        ram[SFR_PSW.x] &= 0xBF

    if ((~(A ^ B)) & (A ^ S)) & 0x80:
        ram[SFR_PSW.x] |= 0x04
    else:
        ram[SFR_PSW.x] &= 0xFB
    ram[SFR_A.x] = S & 0xFF





def init_rs(rs, psw_rs, p):
    p += f";;  set register bank{rs} in psw" 

    p += atl.move(SFR_PSW, atl.I(psw_rs))
    ram[SFR_PSW.x] = psw_rs

    


def init_rn(RN, p):
    p += f";;  load random value into {RN}" 

    value = random.getrandbits(8)

    p += atl.move(atl.D(RN.addr), atl.I(value))
    ram[RN.addr] = value

    


def test_rs(rs, psw_rs, p):    
    a = 0x00
    p += atl.move(SFR_PSW, atl.I(psw_rs))
    p += atl.move(SFR_A, atl.I(a))

    ram[SFR_PSW.x] = psw_rs
    ram[SFR_A.x] = a
    

def test_rn(RN, p):
    p += f"{op_name} A, {RN}"
    do(ram[RN.addr])

    p += atl.aste(SFR_A, atl.I(ram[SFR_A.x]))
    


def test_bound(RN, p):
    A = random.getrandbits(8)
    p += atl.move(SFR_A, atl.I(A))
    ram[SFR_A.x] = A
    for value in ntl.bound(8):
        p += atl.move(atl.D(RN.addr),  atl.I(value))
        p += f"{op_name} A, {RN}"

        do(ram[RN.addr])
        ram[RN.addr] = value
    


for x in range(128):
    p.iter_rn(init_rs, init_rn)
    p.iter_rn(test_rs, test_rn)

p.iter_rn(lambda a,b: "", test_bound)
