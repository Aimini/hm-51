#########################################################
# 2020-01-27 18:19:21
# AI
# ins: DA A
#########################################################

import random

from .. import testutil as u
from ..sim51util import SIMRAM
from ..asmconst import *

p = u.create_test()
ram = SIMRAM()


for x in range(24):
    a = random.getrandbits(8)
    psw = random.getrandbits(8)
    ram.set_direct(SFR_PSW.x, a)
    ram.set_direct(SFR_PSW.x, psw)
    CY = psw & 0x80
    AC = psw & 0x40
    p += f'''
    MOV ACC, {atl.I(a)}
    MOV PSW, {atl.I(psw)}
    DA  A
    '''

    if AC or ((a & 0xF) > 0x9):
        a += 0x6
    if CY or ((a & 0x1F0) > 0x90):
        a += 0x60

    if a > 0xFF:
        ram.set_direct(SFR_PSW.x, ram.get_direct(SFR_PSW.x) | 0x80)
    ram.set_direct(SFR_A.x, a & 0xFF)
    p += atl.aste(SFR_A, atl.I(ram.get_direct(SFR_A.x)))
    p += atl.aste(SFR_PSW, atl.I(ram.get_direct(SFR_PSW.x)))
