#########################################################
# 2020-01-29 11:06:17
# AI
# ins: XCHD A, @Ri
#########################################################

import __util as u
import random
import itertools
from __asmconst import *
from __numutil import numutil as ntl
from __51util import SIMRAM

p = u.create_test()
ram = SIMRAM()


def test_rs(rs, psw_rs, p):
    p += f'MOV PSW, {atl.I(psw_rs)}'
    

def test_ri(RI, p):
    indirect = random.getrandbits(8)
    p += atl.move(atl.D(RI.addr), atl.I(indirect))
    ram.set_direct(RI.addr, indirect)
    
    value = random.getrandbits(8)
    p += atl.move(RI, atl.I(value))
    ram.set_iram(indirect, value)

    a = random.getrandbits(8)
    p += f'''
    MOV ACC, {atl.I(a)}
    XCHD A, {RI}
    '''
    ram.set_direct(SFR_A.x, a)
    # write indirect may overwrite @Rn it self, so we need to get indirect again
    indirect = ram.get_direct(RI.addr)
    b = ram.get_iram(indirect)

    al = a & 0x0F
    bl = b & 0x0F
    a = (a & 0xF0) | bl
    b = (b & 0xF0) | al

    ram.set_direct(SFR_PSW.x, a)
    ram.set_iram(indirect, b)


    p += atl.aste(SFR_A,atl.I(a))
    p += atl.aste(RI, atl.I(ram.get_iram(ram.get_direct(RI.addr))))
    

for x in range(291):
    p.iter_ri(test_rs, test_ri)