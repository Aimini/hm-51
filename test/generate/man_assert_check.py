#########################################################
# 2020-01-08 19:45:35
# AI
# MANUALLY ensure that the assertion functions correctly.
#########################################################

import __util as u
import __asmutil as atl


    
def do(w):
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
    for x in [[atl.I_00, atl.I_00], [atl.I_02, atl.I_40], [atl.I_DE,atl.I_A0]]:
        w(atl.astl(x[0],x[1]) + '\n')
        w(atl.aste(x[0],x[1]) + '\n')
        w(atl.astg(x[0],x[1]) + '\n')
        
u.test(do)