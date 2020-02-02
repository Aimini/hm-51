#########################################################
# 
# for(int i = 0;i  < iter_test_time; ++i )
# {
#   fill ram to random data;
#   for(int rs = 0;rs < 4; ++rs)
#   {
#        for(int ri = 0; ri < 2; ++ ri)
#       {
#           fill random indirect address to ri;
#       }
#       set rs in PSW;
#       set A to A_initial_value;
#       for(int ri = 0; ri < 2; ++ ri)
#       {
#           do opeartion with A and ri;
#           check result in A;
#       }
#   }
# }
#########################################################
import __util as u
from __asmconst import *
from __51util import SIMRAM
import random
from __numutil import numutil as ntl


class XXX_A_Ri:
    def __init__(self, op_name):
        self.ram = SIMRAM()
        self.p = u.create_test()
        self.op_name = op_name

    def op_func(self, B):
        pass

    def gen(self, A_initail_value, iter_test_time, random_test_time):
        ram = self.ram
        p = self.p
        op_func = self.op_func
        op_name = self.op_name

        def init_ram(addr, p):
            p += ";; init ram with random data."
            v = random.getrandbits(8)
            p += atl.move(atl.D(addr), atl.I(v))
            ram.set_direct(addr, v)
            
        def empty_rs(rs, psw_rs, p):
            pass
            


        def init_ri(RI, p):
            indirect = random.getrandbits(7)
            p += atl.move(atl.D(RI.addr), atl.I(indirect))
            ram.set_iram(RI.addr, indirect)
            


        def test_rs(rs, psw_rs, p):    
            a = A_initail_value
            p += atl.move(SFR_PSW, atl.I(psw_rs))
            p += atl.move(SFR_A, atl.I(a))

            ram.set_direct(SFR_PSW.x, psw_rs)
            ram.set_direct(SFR_A.x, a)

        def test_ri(RI, p):
            p += f"{op_name} A, {RI}"
            op_func(ram.get_iram(ram.get_iram(RI.addr)))
            p += atl.aste(SFR_A, atl.I(ram.get_direct(SFR_A.x)))
            


        def test_bound(RI, p):
            A = random.getrandbits(8)
            p += atl.move(SFR_A.x, atl.I(A))
            p += atl.move(SFR_PSW.x,  atl.I(RI.psw_rs))
            ram.set_direct(SFR_A.x, A)
            ram.set_direct(SFR_PSW.x, RI.psw_rs)

            for indirect in ntl.bound(7):
                for value in ntl.bound(8):
                    p += atl.move(atl.D(indirect), atl.I(value))
                    ram.set_iram(indirect, value)

                    p += atl.move(atl.D(RI.addr),  atl.I(indirect))
                    ram.set_iram(RI.addr, indirect)

                    test_ri(RI, p)

            
        for x in range(iter_test_time):
            p.iter_is(init_ram)
            p.iter_ri(empty_rs, init_ri)
            p.iter_ri(test_rs,  test_ri)


        for x in range(random_test_time):
            p.iter_ri(empty_rs, test_bound)