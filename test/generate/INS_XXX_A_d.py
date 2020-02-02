#########################################################
# 
#########################################################

import __util as u
import random
from __asmconst import *
from __numutil import numutil as ntl
from __51util import SIMRAM
import INS_OPERATION

class INS_XXX_A_D():
    def __init__(self, op_name):
        self.ram = SIMRAM()
        self.p = u.create_test()
        self.op_name = op_name


    def gen(self, A_inital_value, iter_test_time):
        p = self.p
        ram = self.ram
        op_name = self.op_name
        op_func = INS_OPERATION.OP_LUT[op_name]
        
        for addr in p.ris():
            for value in ntl.bound(8):
                p += atl.move(atl.D(addr), atl.I(value))
                ram.set_direct(addr, value)

                p += f'{op_name} A, {atl.D(addr)}'
                A = op_func(ram.get_direct(SFR_A.x), ram.get_direct(addr),ram)
                ram.set_direct(SFR_A.x, A)

                p += atl.aste(SFR_A, atl.I(ram.get_direct(SFR_A.x)))

        for no in range(iter_test_time):

            if no % 100 == 0:
                p += ';;; set A to #{hex(A_inital_value)}'
                p += f'MOV ACC, #{hex(A_inital_value)}'
                ram.set_direct(SFR_A.x, A_inital_value)
                
            # load_random_data
            for addr in p.ris():
                value = random.getrandbits(8)
                p += atl.move(atl.D(addr), atl.I(value))
                ram.set_direct(addr, value)
            # execute and check
            for addr in p.ris():
                p += f'{op_name} A, {atl.D(addr)}'
                A = op_func(ram.get_direct(SFR_A.x), ram.get_direct(addr),ram)
                ram.set_direct(SFR_A.x, A)

                p += atl.aste(SFR_A, atl.I(ram.get_direct(SFR_A.x)))