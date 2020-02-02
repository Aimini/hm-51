#########################################################
# 
#########################################################

import __util as u
import random
from __asmconst import *
from __numutil import numutil as ntl
from __51util import SIMRAM

from INS_XXX_A_Rn import XXX_A_RN


class ADD_A_Rn(XXX_A_RN):
    def __init__(self, op_name, use_psw_cy):
        super().__init__(op_name)
        self.use_psw_cy = use_psw_cy

    def op_func(self, B):
        if self.use_psw_cy:
            ci = self.ram.get_bit(SFR_PSW.x, 7)
        else:
            ci = 0
        A = self.ram.get_direct(SFR_A.x)

        SL = (A & 0xF) + (B & 0xF) + ci
        S = A + B + ci

        cy = 1 if S > 0xFF else 0
        self.ram.set_bit(SFR_PSW.x, 7, cy)

        ac = 1 if SL > 0xF else 0
        self.ram.set_bit(SFR_PSW.x, 6, ac)

        ov = 1 if((~(A ^ B)) & (A ^ S)) & 0x80 else 0
        self.ram.set_bit(SFR_PSW.x, 2, ov)

        self.ram.set_direct(SFR_A.x, S & 0xFF)

class SUBB_A_Rn(XXX_A_RN):
    def __init__(self, op_name):
        super().__init__(op_name)

    def op_func(self, B):
        A = self.ram.get_direct(SFR_A.x)
        ci = self.ram.get_bit(SFR_PSW.x, 7)

        SL = (A & 0xF) - (B & 0xF) - ci
        S = A - B - ci

        cy = 1 if S < 0 else 0
        self.ram.set_bit(SFR_PSW.x, 7, cy)

        ac = 1 if SL < 0 else 0
        self.ram.set_bit(SFR_PSW.x, 6, ac)

        ov = 1 if((A ^ B) & (A ^ S)) & 0x80 else 0
        self.ram.set_bit(SFR_PSW.x, 2, ov)

        self.ram.set_direct(SFR_A.x, S & 0xFF)