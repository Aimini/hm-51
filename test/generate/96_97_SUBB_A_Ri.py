#########################################################
# 2020-01-23 12:41:37
# AI
# ins: SUBB A, @Ri
#########################################################
from __asmconst import *
from INS_XXX_A_Ri import XXX_A_Ri
import INS_OPERATION

class SUBB_A_Ri(XXX_A_Ri):
    def __init__(self):
        super().__init__("SUBB")

    def op_func(self, B):
        INS_OPERATION.op_a_subb_xx(self.ram, B)
        

SUBB_A_Ri().gen(0, 61, 1)
