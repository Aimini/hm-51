#########################################################
# 
# for(int i = 0;i  < iter_test_time; ++i )
# {
#   fill IRAM to random data;
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
        # self.test_data = [0xD0]
        # self.test_data_idx = 0

    def op_func(self, B):
        pass
    
    def get_random(self, x):
        # rt = self.test_data[self.test_data_idx]
        # self.test_data_idx += 1
        # self.test_data_idx %= len(self.test_data)
        return random.getrandbits(8)

    def gen(self, A_initail_value, iter_test_time, random_test_time):
        ram = self.ram
        p = self.p
        op_func = self.op_func
        op_name = self.op_name

        def init_iram(addr, p):
            
            v = self.get_random(8)
            #using @R0 to set IRAM
            p += f'''
            ;; init ram with random data.  {hex(addr)} <- #{hex(v)}
            ;; 
            MOV PSW, #0
            '''
            p += atl.move('0x00', atl.I(addr))
            p += atl.move('@R0', atl.I(v))
            ram.set_direct(SFR_PSW.x, 0)
            ram.set_iram(0, addr)
            ram.set_iram(addr, v)
            
        def empty_rs(rs, psw_rs, p):
            pass
            


        def init_ri(RI, p):
            indirect = self.get_random(8)
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
            indirect = ram.get_iram(RI.addr)
            value = ram.get_iram(indirect)
            op_func(value)
            p += atl.aste(SFR_A, atl.I(ram.get_direct(SFR_A.x)))
            


        def test_bound(RI, p):
            A = self.get_random(8)
            p += atl.move(SFR_A.x, atl.I(A))
            p += atl.move(SFR_PSW.x,  atl.I(RI.psw_rs))
            ram.set_direct(SFR_A.x, A)
            ram.set_direct(SFR_PSW.x, RI.psw_rs)

            for indirect in ntl.bound(8):
                for value in ntl.bound(8):
                    
                    p += atl.move(atl.D(RI.addr),  atl.I(indirect))
                    p += atl.move(RI, atl.I(value))
                    ram.set_iram(RI.addr, indirect)
                    ram.set_iram(indirect, value)
                    test_ri(RI, p)
                    

        for x in range(iter_test_time):
            p.iter_iram(init_iram)
            p.iter_ri(empty_rs, init_ri)
            p.iter_ri(test_rs,  test_ri)


        for x in range(random_test_time):
            p.iter_ri(empty_rs, test_bound)