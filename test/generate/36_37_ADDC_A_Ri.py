#########################################################
# 2020-01-23 12:41:37
# AI
# ins: ADDC A, @Ri
#########################################################

from INS_XXX_A_Ri import XXX_A_Ri
import INS_OPERATION

class ADDC_A_Ri(XXX_A_Ri):
    def __init__(self):
        super().__init__("ADDC")

    def op_func(self, B):
        INS_OPERATION.op_a_addc_xx(self.ram, B, True)

ADDC_A_Ri().gen(0, 15, 1)