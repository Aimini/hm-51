#########################################################
# 2020-01-29 14:20:25
# AI
# ins: MOVX @DPTR, A
#########################################################

import __util as u
import random
from __asmconst import *
from __numutil import numutil  as ntl
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
   
    

