#########################################################
# 2020-01-22 22:58:47
# AI
# ins: AND direct, A
#########################################################

import __util as u
import random
from __asmconst import *
from __numutil import numutil as ntl
from __51util import SIMRAM

p = u.create_test()
ram = SIMRAM()


def do(x):
    cy = 0 #(ram[SFR_PSW.x] & 0x80) >> 1
    A = ram[SFR_A.x]
    SL = (A&0xF) + (x&0xF) + cy
    S  =  A  + x + cy

    if S > 0xFF:
        ram[SFR_PSW.x] |= 0x80
    else:
        ram[SFR_PSW.x] &= 0x7F
    
    if SL > 0xF:
        ram[SFR_PSW.x] |= 0x40
    else:
        ram[SFR_PSW.x] &= 0xBF

    if ((~(A ^ x)) & (A ^ S)) & 0x80:
        ram[SFR_PSW.x] |= 0x04
    else:
        ram[SFR_PSW.x] &= 0xFB
    ram[SFR_A.x] = S & 0xFF

operation = "ADD"

for addr in p.ris():
    for value in ntl.bound(8):
        p += atl.move(atl.D(addr), atl.I(value))
        p += f"{operation} A, {atl.D(addr)}"
        ram[addr] = value
        do(ram[addr])

        p += atl.aste(SFR_A, atl.I(ram[SFR_A.x]))

for x in range(16):
    # load_random_data
    for addr in p.ris():
        value = random.getrandbits(8)
        p += atl.move(atl.D(addr), atl.I(value))
        ram[addr] = value

    for addr in p.ris():
        p += f"{operation} A, {atl.D(addr)}"
        do(ram[addr])

        p += atl.aste(SFR_A, atl.I(ram[SFR_A.x]))