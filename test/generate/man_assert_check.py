#########################################################
# 2020-01-08 19:45:35
# AI
# MANUALLY ensure that the assertion functions correctly.
#########################################################

import __util as u
from __asmconst import *


p = u.create_test()
#
# seq:
#  less than
#  equal
#  greater than
#
# who failed:
# 1. lt ,gt
# 2. eq, gt
# 3. lt, eq
for x in [[I_00, I_00], [I_02, I_40], [I_DE, I_A0]]:
    a = x[0]
    b = x[1]
    p(atl.astl(a,b))
    p(atl.aste(a,b))
    p(atl.astg(a,b))