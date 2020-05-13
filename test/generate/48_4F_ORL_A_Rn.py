#########################################################
# 2020-01-23 16:03:11
# AI
# ins: ORL A, Rn
#########################################################
from __asmconst import *
from INS_XXX_A_Rn import XXX_A_RN


class ORL_A_Rn(XXX_A_RN):
    def __init__(self):
        super().__init__('ORL')

    def op_func(self, B):
        A = self.ram.get_direct(SFR_A.x)
        self.ram.set_direct(SFR_A.x, A | B)


ORL_A_Rn() .gen(0, 128, 1)
