#########################################################
# 2020-01-23 12:41:37
# AI
# ins: ADD A, @Ri
#########################################################
from INS_XXX_A_Ri import XXX_A_Ri
import INS_OPERATION

class ADD_A_Ri(XXX_A_Ri):
    def __init__(self):
        super().__init__("ADD")

    def op_func(self, B):
        INS_OPERATION.op_a_addc_xx(self.ram, B, False)

ADD_A_Ri().gen(0, 61, 1)