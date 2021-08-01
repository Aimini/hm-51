#########################################################
# 2020-01-23 16:03:11
# AI
# ins: ORL A, @Rn
#########################################################
from .common import INS_OPERATION
from .common.INS_XXX_A_Rn import XXX_A_RN


class SUBB_A_Rn(XXX_A_RN):
    def __init__(self):
        super().__init__("SUBB")

    def op_func(self, B):
        INS_OPERATION.op_a_subb_xx(self.ram, B)


p = SUBB_A_Rn().gen(0, 127, 1)
