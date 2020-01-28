#########################################################
# 2020-01-28 11:36:00
# AI
# ins: MOV direct, A
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
    MOV ACC, {atl.I(value)}
    MOV {atl.D(addr)}, A
    '''
    ram[SFR_A.x] = value
    ram[addr] = ram[SFR_A.x]
    return ""

def one():
    p.iter_is(fill_one)
    for addr in p.ris():
        atl.aste(atl.D(addr), atl.I(ram[addr]))

for _ in range(64):
    one()