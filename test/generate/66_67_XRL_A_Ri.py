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

op_name = "XRL"


def op(a, b): return a ^ b


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
    ram[SFR_A.x] = op(ram[SFR_A.x], ram[ram[RI.addr]])

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

            ram[SFR_A.x] = op(ram[SFR_A.x], ram[indirect])
            ram[indirect] = value
            ram[RI.addr] = indirect
    


for x in range(64):
    p.iter_is(init_ram)
    p.iter_ri(init_rs, init_ri)
    p.iter_ri(test_rs, test_ri)

p.iter_ri(lambda a,b: "", test_bound)
