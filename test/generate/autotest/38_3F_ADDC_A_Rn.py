#########################################################
# 2020-01-23 16:03:11
# AI
# ins: ADDC A, Rn
#########################################################

from .common import INS_OPERATION
from .common.INS_XXX_A_Rn import XXX_A_RN


class ADDC_A_Rn(XXX_A_RN):
    def __init__(self):
        super().__init__("ADDC")

    def op_func(self, B):
        INS_OPERATION.op_a_addc_xx(self.ram, B, True)


p = ADDC_A_Rn().gen(0, 128, 1)
