#########################################################
# 2020-01-23 16:03:11
# AI
# ins: XRL A, Rn
#########################################################

from .common.INS_XXX_A_Rn import XXX_A_RN
from ..asmconst import *


class XRL_A_Rn(XXX_A_RN):
    def __init__(self):
        super().__init__('XRL')

    def op_func(self, B):
        A = self.ram.get_direct(SFR_A.x)
        self.ram.set_direct(SFR_A.x, A ^ B)


p = XRL_A_Rn() .gen(0, 128, 1)
