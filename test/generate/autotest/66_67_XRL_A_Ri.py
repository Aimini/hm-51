#########################################################
# 2020-01-23 12:41:37
# AI
# ins: XRL A, @Ri
#########################################################

from .common.INS_XXX_A_Ri import XXX_A_Ri
from ..asmconst import *


class XRL_A_Ri(XXX_A_Ri):
    def __init__(self):
        super().__init__("XRL")

    def op_func(self, B):
        A = self.ram.get_direct(SFR_A.x)
        self.ram.set_direct(SFR_A.x, A ^ B)
        

p = XRL_A_Ri().gen(0, 15, 1)