#########################################################
# 2020-01-08 19:45:35
# AI
# ins: MOV direct, #immed.
# how: write address of the iram and SFR into itself.
#########################################################

import __util as u
import __asmutil as atl

def one(*vargs):
    addr = vargs[0]
    # set memory cells' value to it's address
    return atl.move(atl.D(addr),atl.I(addr))

    
def do(w):
    def wone(*vargs):
        w(one(*vargs))
    
    u.sdirect(wone)

u.test(do)