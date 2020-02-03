#########################################################
# 2020-01-28 14:01:44
# AI
# ins: MOV A, @Ri
#########################################################

from __asmconst import *
from INS_XXX_A_Ri import XXX_A_Ri
import INS_OPERATION

class MOV_A_Ri(XXX_A_Ri):
    def __init__(self):
        super().__init__("MOV")

    def op_func(self, B):
        self.ram.set_direct(SFR_A.x, B)
        

MOV_A_Ri().gen(0, 15, 1)