#########################################################
# 2020-01-08 19:45:35
# AI
# ins: MOV direct, #immed.
# how: write address of the iram and SFR into itself.
#########################################################

import __util as u
ntl = u.numutil

def one(*vargs):
    addr = vargs[0]
    # set memory cells' value to it's address
    return u.ins("MOV", ntl.direct(addr),ntl.immed(addr))

    
def do(fh,w):
    def wone(*vargs):
        w(one(*vargs))
        w('\n')

    u.sdirect(wone)

u.test(do)