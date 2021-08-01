#########################################################
# 2020-01-29 15:35:24
# AI
# ins: MOVX A, @Ri
#########################################################


import random

from .. import testutil as u
from ..asmconst import *

p = u.create_test()

XRAM = list(range(0x10000))
used_xaddress = []

count = 256
def test_rs(rs, psw_rs, p):
    p += f'MOV  PSW, #{psw_rs}'
    

def test_ri(RI, p):
    a = random.getrandbits(8)
    xaddr = random.getrandbits(8)
    used_xaddress.append(xaddr)
    
    p += f'''
    MOV  {RI.addr}, #{xaddr}
    MOV  ACC, #{a}
    MOVX {RI}, A
    '''
    XRAM[xaddr] = a
    

for x in range(count):
    p.iter_ri(test_rs, test_ri)

p.iter_ri(test_rs, test_ri)

for xaddr in used_xaddress:
    rs = random.randrange(4)
    ri = random.randrange(2)
    RI = atl.RI(rs, ri)

    p += f''' 
    MOV  PSW, #{rs << 3}
    MOV  {RI.addr}, #{xaddr}
    MOVX A, {RI}
    '''
    
    p += atl.aste(SFR_A, atl.I(XRAM[xaddr]))
   
    

