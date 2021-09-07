#########################################################
# 2021-08-08 14:21:32
# AI
# test programming ROM function
# this test code are only suit for the simulator,
# the real hardware has timing constraints.
#########################################################

import random

from .. import testutil as u
from ..asmconst import *
from ..numutil import numutil as ntl
SEQ_DISALBE_SDP =(
    (0xAA, 0x5555),(0x55, 0x2AAA),(0x80, 0x5555),
    (0xAA, 0x5555),(0x55, 0x2AAA),(0x20, 0x5555))
SEQ_ENALBE_SDP = (
    (0xAA, 0x5555),(0x55, 0x2AAA),(0xA0, 0x5555))
p = u.create_test()
tWC = 5000
D_tWCL = D_1B
D_tWCH = D_1C
D_SIZE = D_1D
D_PCL = D_1E
D_PCH = D_1F
addr_DATA_CHUCK = 0x20

# 0x1000 - 0xFEFF are reserved for test_code
test_addresses = (0, 128, 0xFF00)
test_block_size = [1,2, 64, 100, 127, 128]
test_block_size.append(128)

# print(test_block_size)
def micro_program(code):
    return f'''
    {atl.move(SFR_A, atl.I(code))}
    {atl.move(SFR_B, atl.I(0xFF ^ code))}
    DB 0xA5
    '''
def write_byte_addr_pair(seq):
    s = ''
    s += atl.move(D_SIZE, atl.I(len(seq)))
    s += '\n'
    i = 0
    start_addr = D_SIZE.x + 1
    for data, addr in seq:
        s += atl.move( atl.D(start_addr + i), atl.I(data))
        s += '\n'
        i += 1
        s += atl.move( atl.D(start_addr + i), atl.I(addr & 0xFF))
        s += '\n'
        i += 1
        s += atl.move( atl.D(start_addr + i), atl.I(addr >> 8))
        s += '\n'
        i += 1
    return s


def programmingPage():
    return micro_program(0x00)

def enableSDP():
    s = write_byte_addr_pair(SEQ_ENALBE_SDP)
    return s + micro_program(0x01)
    
def disableSDP():
    s = write_byte_addr_pair(SEQ_DISALBE_SDP)
    return s + micro_program(0x01)


def write_one_chuck(p, block_size):
    data = list(range(block_size))
    random.shuffle(data)
    for start_addr in test_addresses:
        p += f'\n\n;; ------------------------------------------------ size: {ntl.sx2(block_size)} address: {ntl.sx2(start_addr)}'
        
        
        p += atl.move(D_SIZE, atl.I(block_size))  # block size
        p += atl.move(D_PCL , atl.I(start_addr & 0xFF))
        p += atl.move(D_PCH , atl.I(start_addr >> 8))
        
        p += "MOV R0, #0x20"
        for i, d in enumerate(data):
            p += atl.move("@R0", atl.I(d))
            p += "INC R0"

        p += 'LCALL ROM_PROGRAMMING_PAGE'
        
        p += f'MOV DPTR, #{ntl.sx4(start_addr)}' 
        for i, d in enumerate(data):
            p += f"""
                ;;;  ----------- {i} -------
                ;;assert ROM[{i + start_addr}] == {d}
                
                CLR A
                MOVC A, @A+DPTR
                INC DPTR
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
        p += atl.move('R0', atl.I(addr_DATA_CHUCK))
        p += atl.move('@R0', atl.I(d))
        p += 'LCALL ROM_PROGRAMMING_PAGE'

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
p += f"""
CSEG AT 0x0
MOV     PSW, #0x02
MOV     DPTR,#0xFF00
;; load tWC
MOV     {D_tWCL}, #{tWC & 0xFF}
MOV     {D_tWCH}, #{tWC >> 8}
LJMP TEST_CODE

CSEG AT 0x01000
ROM_PROGRAMMING_PAGE:
{programmingPage()}
RET
TEST_CODE:
"""
p += disableSDP()
for block_size in test_block_size:
    write_one_chuck(p, block_size)

write_one_byte_no_align64(p, 0, 256)

