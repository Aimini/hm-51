#########################################################
# 2020-01-22 13:38:48
# AI
# ins: ADDC A, #immed
#########################################################

import random

from .. import testutil as u
from ..sim51util import SIMRAM
from ..asmconst import *

p = u.create_test()
ram = SIMRAM()

# load_random_data
for addr in p.rdirect():
    value = random.getrandbits(8)
    ram.set_direct(addr, value)
    p += atl.move(atl.D(addr), atl.I(value))


for x in range(32):
    for addr in p.rdirect():
        value = random.getrandbits(8)
        p += f"ORL {atl.D(addr)}, {atl.I(value)}"
        ram.set_direct(addr, ram.get_direct(addr) | value)
        p += atl.aste(atl.D(addr), atl.I(ram.get_direct(addr)))