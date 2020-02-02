#########################################################
# 2020-01-23 12:41:37
# AI
# ins: ORL A, @Ri
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


def init_ram(addr, p):
    p += ";; init ram with random data."
    v = random.getrandbits(8)
    p += atl.move(atl.D(addr), atl.I(v))
    ram[addr] = v
    


def init_rs(rs, psw_rs, p):
    p += ";; load random indirect address to ri" 
    p += atl.move(SFR_PSW, atl.I(psw_rs))
    ram[SFR_PSW.x] = psw_rs
    


def init_ri(RI, p):
    indirect = random.getrandbits(7)
    p += atl.move(atl.D(RI.addr), atl.I(indirect))
    ram[RI.addr] = indirect
    


def test_rs(rs, psw_rs, p):    
    a = 0xFF
    p += atl.move(SFR_PSW, atl.I(psw_rs))
    p += atl.move(SFR_A, atl.I(a))

    ram[SFR_PSW.x] = psw_rs
    ram[SFR_A.x] = a
    

def test_ri(RI, p):

    p += f"{op_name} A, {RI}"
    do(ram[ram[RI.addr]])

    p += atl.aste(SFR_A, atl.I(ram[SFR_A.x]))
    


def test_bound(RI, p):
    A = random.getrandbits(8)
    p += atl.move(SFR_A, atl.I(A))
    ram[SFR_A.x] = A
    for indirect in ntl.bound(7):
        for value in ntl.bound(8):
            p += atl.move(atl.D(indirect), atl.I(value))
            p += atl.move(atl.D(RI.addr),  atl.I(indirect))
            p += f"{op_name} A, {RI}"

            do(ram[indirect])
            ram[indirect] = value
            ram[RI.addr] = indirect
    


for x in range(64):
    p.iter_is(init_ram)
    p.iter_ri(init_rs, init_ri)
    p.iter_ri(test_rs, test_ri)

p.iter_ri(lambda a,b: "", test_bound)
