#########################################################
# 2020-01-23 16:03:11
# AI
# ins: ADDC A, Rn
#########################################################

from INS_XXX_A_Rn import XXX_A_RN
import INS_OPERATION


class ADD_A_Rn(XXX_A_RN):
    def __init__(self):
        super().__init__("ADD")

    def op_func(self, B):
        INS_OPERATION.op_a_addc_xx(self.ram, B, False)


ADD_A_Rn().gen(0, 128, 1)
