#########################################################
# 2021-08-08 14:21:32
# AI
# test programming ROM function
#########################################################

import random

from .. import testutil as u
from ..asmconst import *
from ..numutil import numutil as ntl

p = u.create_test()

D_SIZE = D_00
D_PCL = D_01
D_PCH = D_02
addr_DATA_CHUCK = 3

# 0x1000 - 0xFEFF are reserved for test_code
test_addresses = (0, 64, 0xFF00)
test_block_size = ntl.bound(6)  # 64
test_block_size = list(test_block_size)
test_block_size.remove(0)
# print(test_block_size)


def write_one_chuck(p, block_size):
    data = list(range(block_size))
    random.shuffle(data)
    for start_addr in test_addresses:
        p += f'\n\n;; ------------------------------------------------ size: {ntl.sx2(block_size)} address: {ntl.sx2(start_addr)}'
        
        
        p += atl.move(D_SIZE, atl.I(block_size))  # block size
        p += atl.move(D_PCL , atl.I(start_addr & 0xFF))
        p += atl.move(D_PCH , atl.I(start_addr >> 8))
        
        for i, d in enumerate(data):
            p += atl.move(atl.D(addr_DATA_CHUCK + i), atl.I(d))

        p += 'DB 0xA5'

        for i, d in enumerate(data):
            p += f"""
                MOV DPTR, #{ntl.sx4(start_addr + i)} 
                CLR A
                MOVC A, @A+DPTR
                """
            p += atl.aste(SFR_A, atl.I(d))


def write_one_byte_no_align64(p, start_address, data_size):
    data = list(range(data_size))
    random.shuffle(data)

    p += f'\n\n;; ------------------------------------------------ size: {ntl.sx2(data_size)} address: {ntl.sx2(start_address)}'
    for i, d in enumerate(data):
        addr = start_address + i
        p += atl.move(D_SIZE,atl.I(1))  # block size
        p += atl.move(D_PCL, atl.I(addr & 0xFF))
        p += atl.move(D_PCH, atl.I(addr >> 8))
        p += atl.move(atl.D(addr_DATA_CHUCK), atl.I(d))
        p += 'DB 0xA5'

    for i, d in enumerate(data):
        p += f"""
            MOV DPTR, #{ntl.sx4(start_address + i)} ;block size
            CLR A
            MOVC A, @A+DPTR
            """
        p += atl.aste(SFR_A, atl.I(d))


p.is_prepend_clear_iram = False
p.is_prepend_clear_reg = False
p.is_append_dump = False
p += """
CSEG AT 0x0
MOV PSW, #0x02
MOV DPTR,#0xFF00
LJMP TEST_CODE
CSEG AT 0x01000
TEST_CODE:
"""
for block_size in test_block_size:
    write_one_chuck(p, block_size)

write_one_byte_no_align64(p, 0, 256)
