#########################################################
# 2020-01-28 11:36:00
# AI
# ins: MOV direct, A
#########################################################

import random

from .. import testutil as u
from ..sim51util import SIMRAM
from ..asmconst import *

p = u.create_test()
ram = SIMRAM()

def fill_one(addr, p):
    value = random.getrandbits(8)
    p += f'''
    MOV ACC, {atl.I(value)}
    MOV {atl.D(addr)}, A
    '''
    ram.set_direct(SFR_A.x, value)
    ram.set_direct(addr, ram.get_direct(SFR_A.x))
    

def one():
    p.iter_direct(fill_one)
    for addr in p.rdirect():
        atl.aste(atl.D(addr), atl.I(ram.get_direct(addr)))

for _ in range(64):
    one()