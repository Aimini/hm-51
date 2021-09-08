#########################################################
# 2020-01-28 17:25:15
# AI
# ins: MOV A, Rn
#########################################################
from .common.INS_XXX_A_Rn import XXX_A_RN
from ..asmconst import *


class MOVD_A_Rn(XXX_A_RN):
    def __init__(self):
        super().__init__("MOV")

    def op_func(self, B):
        self.ram.set_direct(SFR_A.x ,B)


p = MOVD_A_Rn().gen(0, 128, 1)