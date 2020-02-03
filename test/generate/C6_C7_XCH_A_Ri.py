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
    

def test_ri(RI, p):
    indirect = random.getrandbits(8)

    p += f'''
    MOV {atl.D(RI.addr)}, {atl.I(indirect)}
    XCH A, {RI}
    '''
    ram.set_direct(RI.addr, indirect)
    
    # swap
    temp = ram.get_direct(SFR_A.x)
    ram.set_direct(SFR_A.x, ram.get_iram(indirect))
    ram.set_iram(indirect, temp)

    RRI = atl.RI(RI.rs, (RI.ri + 1) % 2)
    p += f'MOV {atl.D(RRI.addr)}, {atl.I(indirect)}'
    ram.set_direct(RRI.addr, indirect)

    p += atl.aste(SFR_A, atl.I(ram.get_direct(SFR_A.x)))
    p += atl.aste(RRI, atl.I(ram.get_iram(indirect)))
    


def one(p):
    # inital iram by using @R0
    p += 'MOV PSW, #0'
    ram.set_direct(SFR_PSW.x, 0)
    for iaddr in p.riram():
        value = random.getrandbits(8)
        p += f'MOV 0x00, #{hex(iaddr)}'
        p += f'MOV @R0, #{hex(value)}'
        ram.set_direct(0, iaddr)
        ram.set_iram(iaddr,value)

    p.iter_ri(test_rs, test_ri)

for _ in range(44):
    one(p)