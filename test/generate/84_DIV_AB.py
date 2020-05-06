#########################################################
# 2020-01-31 22:41:47
# AI
# ins: DIV AB
#########################################################
import __util as u
import random
import itertools
from __asmconst import *
from __numutil import numutil as ntl
from __51util import SIMRAM
p = u.create_test()
ram = SIMRAM()


def one(a, b, p):
    p += f'''
            MOV ACC, #{a}
            MOV B, #{b}
            DIV AB
            '''

    if b == 0:
        p += f'''
            MOV ACC, #0
            MOV B, #0
            DIV AB
            '''
        ov = 1
        pf = 0

    else:
        q = a//b
        r = a % b
        
        ov = 0
        pf = bin(q).count('1') & 1

        p += atl.aste(SFR_A, atl.I(q))
        p += atl.aste(SFR_B, atl.I(r))

    psw = pf | ( ov << 2)
    p += atl.aste(SFR_PSW, atl.I(psw))
one(1, 0, p)
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