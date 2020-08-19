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

def get_int_add(no):
    return no + 1

def clear_int(no):    
    l = [0x2, 0x20, 0x8, 0x80]
    if no < 4:
        m = 0xFF & (~l[no])
        return f'ANL TCON, #{m}'
    elif no == 5:
        return f'ANL SCON, #0xFE'
    raise Exception("unsupport interrupt number")

def check_int_cleared(no):
    l = [0x2, 0x20, 0x8, 0x80]
    m = l[no]
    s = f'''
    ;;- check if int cleared
    MOV B, TCON
    ANL B, #{hex(m)}
    '''
    s += atl.aste(SFR_B, atl.I(0))
    return s


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
            LCALL INT_{i}
            RET
        '''
    for i in range(total):
        s += f'''
        INT_{i}:
            ADD A,  #{get_int_add(i)}
            MOV R0, SP
            DEC R0
            MOV B, @R0  ;; move interrupt vector to B
            ;; (B - 3) beacuse LCALL is 3 bytes instruction
            DEC B
			DEC B
			DEC B
            RET ; don't use RETI
        '''
    return s



def test_one(no, ip ,total, p):
    for test_no in range(total):
        for test_ip in range(2):
            p += f';;;;;;;;;;;; {no}, {ip} compare {test_no}, {test_ip}'
            p += 'MOV B, #0'
            p += set_ip(test_no, test_ip)
            p += set_int(test_no)

            if test_ip > ip:
                p += f';;;;;;; -- higer'
                global A    
                A = A + get_int_add(test_no)
                p += atl.aste(SFR_B, atl.I((test_no << 3) + 3))
                p += check_int_cleared(test_no)
                p += atl.aste(SFR_A, atl.I(A))
                p += 'LCALL EXIT_ISR'
            else:
                p += f';;;;;;; -- lower'
                p += clear_int(test_no)
                p += atl.aste(SFR_A, atl.I(A))


p.is_prepend_clear_reg = False
p.is_prepend_clear_iram = False
test_int_num = 4
p += 'LJMP START'
p += get_isr(test_int_num)
p += '''
EXIT_ISR:
    RETI

START:'''
p += atl.clear_reg()
p += atl.clear_iram()
p += '''
MOV IE, #0x8F
MOV TCON, #0x05
'''
for no in range(test_int_num):
    for ip in range(2):
        p += f';;;;;;; ------------------ test for {no}, {ip} ------------------'
        p += set_ip(no, ip)
        p += set_int(no)
        A += get_int_add(no)
        test_one(no, ip, test_int_num, p)
        p += 'LCALL EXIT_ISR'
