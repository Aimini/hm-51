#########################################################
# 2020-01-29 15:17:04
# AI
# ins: MOVX A, @DPTR
# copy of F0_MOVX_DPTR_A.py
#########################################################

import random

from .. import testutil as u
from ..asmconst import *

p = u.create_test()

XRAM = list(range(0x10000))
used_xaddress = []
# init XRAM
count = 0x800
for i in range(count):    
    a = random.getrandbits(8)
    xaddr = random.getrandbits(16)
    used_xaddress.append(xaddr)
    dpl = xaddr & 0xFF
    dph = xaddr >> 8
    
    p += f'''
    MOV  DPL, #{dpl}
    MOV  DPH, #{dph}
    MOV  ACC, #{a}
    MOVX @DPTR, A
    '''
    XRAM[xaddr] = a

# sum
for xaddr in used_xaddress:    
    dpl = xaddr & 0xFF
    dph = xaddr >> 8
    
    p += f'''
    MOV  DPL, #{dpl}
    MOV  DPH, #{dph}
    MOV  ACC, #{a}
    MOVX A, @DPTR
    '''
    
    p += atl.aste(SFR_A, atl.I(XRAM[xaddr]))
   
    

