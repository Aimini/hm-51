#########################################################
# 
#########################################################

import __util as u
import random
from __asmconst import *
from __numutil import numutil as ntl
from __51util import SIMRAM


class XXX_A_RN:
    def __init__(self, op_name):
        self.ram = SIMRAM()
        self.p = u.create_test()
        self.op_name = op_name

    def op_func(self, B):
        pass

    def gen(self, iter_test_time, random_test_time):
        ram = self.ram
        p = self.p
        op_func = self.op_func
        op_name = self.op_name

        def empty_rs(rs, psw_rs, p):
            pass

        def init_rn(RN, p):
            p += f';;  load random value into {RN}'
            value = random.getrandbits(8)

            p += atl.move(atl.D(RN.addr), atl.I(value))
            ram.set_iram(RN.addr, value)

        def test_rs(rs, psw_rs, p):
            a = 0x00
            p += atl.move(SFR_PSW, atl.I(psw_rs))
            p += atl.move(SFR_A, atl.I(a))

            ram.set_direct(SFR_PSW.x, psw_rs)
            ram.set_direct(SFR_A.x, a)

        def test_rn(RN, p):
            p += f'{self.op_name} A, {RN}'
            op_func(ram.get_iram(RN.addr))
            p += atl.aste(SFR_A, atl.I(ram.get_direct(SFR_A.x)))
        
        def test_bound(RN, p):
            A = random.getrandbits(8)
            p += atl.move(SFR_PSW.x, atl.I(RN.psw_rs))
            ram.set_direct(SFR_PSW.x, RN.psw_rs)
            p += atl.move(SFR_A, atl.I(A))
            ram.set_direct(SFR_A.x, A)

            for value in ntl.bound(8):
                p += atl.move(atl.D(RN.addr),  atl.I(value))
                ram.set_iram(RN.addr, value)

                p += f'{self.op_name} A, {RN}'
                op_func(ram.get_iram(RN.addr))

                p += atl.aste(SFR_A, atl.I(ram.get_direct(SFR_A.x)))
            
            
        for x in range(iter_test_time):
            p.iter_rn(empty_rs, init_rn)
            p.iter_rn(test_rs,  test_rn)

        for x in range(random_test_time):
            p.iter_rn(empty_rs, test_bound)
