#########################################################
# 2020-01-23 16:03:11
# AI
# ins: XRL A, Rn
#########################################################

from __asmconst import *
from INS_XXX_A_Rn import XXX_A_RN

class XRL_A_Rn(XXX_A_RN):
    def op_func(self, B):
        A = self.ram.get_direct(SFR_A.x)
        self.ram.set_direct(SFR_A.x, A ^ B)


tt = XRL_A_Rn("XRL")
tt.gen(128,1)

