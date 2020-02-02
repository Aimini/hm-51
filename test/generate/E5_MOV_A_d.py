#########################################################
# 2020-01-28 12:03:11
# AI
# ins: MOV A, direct
#########################################################

import random
import __util as u
from __asmconst import *
from __51util import SIMRAM

p = u.create_test()
ram = SIMRAM()

def fill_one(addr, p):
    value = random.getrandbits(8)
    p += f'''
    MOV {atl.D(addr)}, {atl.I(value)}
    MOV A, {atl.D(addr)}
    '''
    ram[addr] = value
    ram[SFR_A.x] = ram[addr]
    p += atl.aste(SFR_A, atl.I(ram[SFR_A.x]))
    

def one():
    p.iter_is(fill_one)

for _ in range(32):
    one()