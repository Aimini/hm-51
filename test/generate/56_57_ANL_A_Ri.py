#########################################################
# 2020-01-23 12:41:37
# AI
# ins: ANL A, @Ri
#########################################################

from __asmconst import *
from INS_XXX_A_Ri import XXX_A_Ri
import INS_OPERATION

class ANL_A_Ri(XXX_A_Ri):
    def __init__(self):
        super().__init__("ANL")

    def op_func(self, B):
        A = self.ram.get_direct(SFR_A.x)
        self.ram.set_direct(SFR_A.x, A & B)
        

ANL_A_Ri().gen(0xFF, 15, 1)