#########################################################
# 2020-01-28 12:24:37
# AI
# ins: XCH A, direct
#########################################################

import random
import __util as u
from __asmconst import *
from __51util import SIMRAM

p = u.create_test()
ram = SIMRAM()

def fill_one(addr, p):
    a =  random.getrandbits(8)
    value = random.getrandbits(8)
    p += f'''
    MOV ACC, {atl.I(a)}
    MOV {atl.D(addr)}, {atl.I(value)}
    XCH A, {atl.D(addr)}
    '''
    ram[SFR_A.x] = a
    ram[addr] = value
    # swap
    temp = ram[SFR_A.x]
    ram[SFR_A.x] = ram[addr]
    ram[addr] = temp

    p += atl.aste(SFR_A, atl.I(ram[SFR_A.x]))
    p += atl.aste(addr, atl.I(ram[addr]))
    

def one():
    p.iter_is(fill_one)

for _ in range(16):
    one()