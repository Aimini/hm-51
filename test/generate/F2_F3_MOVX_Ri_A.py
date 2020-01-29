#########################################################
# 2020-01-29 18:20:21
# AI
# ins: MOVX @Ri, A
# copy of E2_E3_MOVX_A_Ri.py
#########################################################


import __util as u
import random
from __asmconst import *
from __numutil import numutil  as ntl
p = u.create_test()

XRAM = list(range(0x10000))
used_xaddress = []

count = 256
def test_rs(rs, psw_rs, p):
    p += f'MOV  PSW, #{psw_rs}'
    return ''

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
    return ''

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
   
    

