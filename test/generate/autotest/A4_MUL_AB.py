#########################################################
# 2020-01-29 18:36:59
# AI
# ins: MUL AB
#########################################################
import random

from .. import testutil as u
from ..sim51util import SIMRAM
from ..asmconst import *
from ..numutil import numutil as ntl

p = u.create_test()
ram = SIMRAM()


def one(a, b, p):
    r = a*b
    ra = r & 0xFF
    rb = r >> 8
    p += f'''
        MOV ACC, #{a}
        MOV B, #{b}
        MUL AB
        '''
    p += atl.aste(SFR_A, atl.I(ra))
    p += atl.aste(SFR_B, atl.I(rb))

one(9, 24, p)
p += atl.dump()

for a in ntl.bound(8):
    for b in ntl.bound(8):
        one(a, b, p)

for _ in range(1024):
    a = random.getrandbits(8)
    b = random.getrandbits(8)
    one(a, b, p)

    if _ % 50 == 0:
        p += atl.dump()