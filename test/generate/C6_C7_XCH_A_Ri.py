#########################################################
# 2020-01-28 14:09:05
# AI
# ins: XCH A, @Ri
#########################################################

import random
import __util as u
from __asmconst import *
from __51util import SIMRAM

p = u.create_test()
ram = SIMRAM()
def test_rs(rs,psw_rs,p):
    p += f'MOV PSW, {atl.I(psw_rs)}'
    return ""

def test_ri(RI, p):
    indirect = random.getrandbits(7)

    p += f'''
    MOV {atl.D(RI.addr)}, {atl.I(indirect)}
    XCH A, {RI}
    '''
    ram[RI.addr] = indirect
    
    # swap
    temp = ram[SFR_A.x]
    ram[SFR_A.x] = ram[ram[RI.addr]]
    ram[ram[RI.addr]] = temp

    p += atl.aste(SFR_A, atl.I(ram[SFR_A.x]))
    p += atl.aste(atl.D(indirect), atl.I(ram[indirect]))
    return ""
    
def init_ram(addr, p):
    value = random.getrandbits(8)
    p += atl.move(atl.D(addr), atl.I(value))
    ram[addr] = value
    return ""

def one():
    p.iter_is(init_ram)
    p.iter_ri(test_rs, test_ri)

for _ in range(16):
    one()