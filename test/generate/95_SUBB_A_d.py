#########################################################
# 2020-01-23 22:46:36
# AI
# ins: SUBB A,direct
#########################################################

import __util as u
import random
from __asmconst import *
from __numutil import numutil as ntl
from __51util import SIMRAM

p = u.create_test()
ram = SIMRAM()


def do(B):
    cy = (ram[SFR_PSW.x] & 0x80) >> 7
    A = ram[SFR_A.x]
    SL = (A & 0xF) - (B & 0xF) - cy
    S = A - B - cy

    if S < 0:
        ram[SFR_PSW.x] |= 0x80
    else:
        ram[SFR_PSW.x] &= 0x7F

    if SL < 0:
        ram[SFR_PSW.x] |= 0x40
    else:
        ram[SFR_PSW.x] &= 0xBF

    if ((A ^ B) & (A ^ S)) & 0x80:
        ram[SFR_PSW.x] |= 0x04
    else:
        ram[SFR_PSW.x] &= 0xFB
    ram[SFR_A.x] = S & 0xFF


operation = "SUBB"

for addr in p.ris():
    for value in ntl.bound(8):
        p += atl.move(atl.D(addr), atl.I(value))
        p += f"{operation} A, {atl.D(addr)}"
        ram[addr] = value
        do(ram[addr])

        p += atl.aste(SFR_A, atl.I(ram[SFR_A.x]))

    p += atl.dump(f"at addr {atl.D(addr)}")

for x in range(16):
    # load random data
    for addr in p.ris():
        value = random.getrandbits(8)
        p += atl.move(atl.D(addr), atl.I(value))
        ram[addr] = value

    for addr in p.ris():
        p += f"{operation} A, {atl.D(addr)}"
        do(ram[addr])

        p += atl.aste(SFR_A, atl.I(ram[SFR_A.x]))
