#########################################################
# 2020-01-08 19:45:35
# AI
# ins: MOV direct, #immed.
# how: write address of the iram and SFR into itself.
#########################################################

import __util as u
from __asmconst import *

p = u.create_test()


p.iter_is(lambda  addr: atl.move(atl.D(addr), atl.I(addr)))

# move to self
#### IRAM 0,1,2,3...0x7E, 0x7F
#### SFR  0x81, 0x82, 0x83, 0xA8, 0xB8, 0xD1(PF in PSW, not 0xD0), 0xE0, 0xF0,
p += ";;;;;;;;;;;;;;;;;;;;;; move to self"
p.iter_is(lambda  addr: atl.move(atl.D(addr), atl.D(addr)))



# mirror content in IRAM
#### IRAM 0x7F, 0x7E, 0x7D ... 0x7D,0x7E,0x7F
#### SFR  0x81, 0x82, 0x83, 0xA8, 0xB8, 0xD1, 0xE0, 0xF0,
p += ";;;;;;;;;;;;;;;;;;;;;; mirror iram"
p.iterx_iram(lambda a,b: atl.move(atl.D(a), atl.D(b)))

# some complicate
#### IRAM 0x81, 0x82, 0x83, 0xA8, 0xB8, 0xD1, 0xE0, 0xF0,    0x77 ... 3,2,1,0
#### SFR  0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 
p += ";;;;;;;;;;;;;;;;;;;;;; swap part sfr and iram"
for i, v in enumerate(p.rsfr()):
    #  move RAM[i] <- SFR[i]
    p += atl.move(atl.D(i), atl.D(v))
    #  move SFR[i] <- RAM[0x40 + i]
    p += atl.move(atl.D(v), atl.D(0x40 + i))

# mirror content in SFR
#### IRAM 0x81, 0x82, 0x83, 0xA8, 0xB8, 0xD1(PSW ops), 0xE0, 0xF0, 0x77 ... 3,2,1,0
#### SFR  0x47, 0x46, 0x45, 0x44, 0x44, 0x45, 0x46, 0x47, 
p += ";;;;;;;;;;;;;;;;;;;;;; swap sfr"
p.iterx_sfr(lambda a,b: atl.move(atl.D(a), atl.D(b)))