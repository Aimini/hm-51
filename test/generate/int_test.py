#########################################################
# 2020-02-08 12:36:35
# AI
# test interrupt
#########################################################

import __util as u
import random
from __asmconst import *
from __numutil import numutil  as ntl
p = u.create_test()

def set_int(no):
    l = [0x2, 0x20, 0x8, 0x80]
    if no < 4:
        return f'ORL TCON, #{l[no]}'
    elif no == 5:
        return f'ORL SCON, #1'
    raise Exception("unsupport interrupt number")

def clear_int(no):    
    l = [0x2, 0x20, 0x8, 0x80]
    if no < 4:
        m = 0xFF & (~l[no])
        return f'ANL TCON, #{m}'
    elif no == 5:
        return f'ANL SCON, #0xFE'
    raise Exception("unsupport interrupt number")


def set_ip(idx, val):
    if val > 0:
        return f'ORL IP, #{hex(1 << idx)}'
    else:
        mask = (~(1 << idx)) & 0xFF
        return f'ANL IP, #{hex(mask)}'
A = 0
def get_isr(total):
    s = ''
    for i in range(total):
        s += f'''
        CSEG AT {hex((i << 3) + 3)}
        ADD A,  #{i}
        RET ; don't use RETI
        '''
    return s

def test_one(no, ip ,total, p):
    for test_no in range(total):
        for test_ip in range(2):
            p += f';;;;;;;;;;;; {no}, {ip} compare {test_no}, {test_ip}'
            p += set_ip(test_no, test_ip)
            p += set_int(test_no)
            if test_ip > ip:
                p += f';;;;;;; -- higer'
                global A    
                A = A + test_no
                p += 'LCALL EXIT_ISR'
            else:
                p += f';;;;;;; -- lower'
            p += clear_int(test_no)
            p += atl.aste(SFR_A, atl.I(A))

p.is_prepend_clear_reg = False

test_int_num = 4
p += 'LJMP START'
p += get_isr(test_int_num)
p += '''
EXIT_ISR:
    RETI

START:'''
p += atl.clear_reg()
p += '''
MOV IE, #0x8F
MOV TCON, #0x05
'''
for no in range(test_int_num):
    for ip in range(2):
        p += f';;;;;;; ------------------ test for {no}, {ip} ------------------'
        p += set_ip(no, ip)
        p += set_int(no)
        A += no
        test_one(no, ip, test_int_num, p)
        p += 'LCALL EXIT_ISR'
