#########################################################
# 2020-01-27 19:32:31
# AI
# ins: LCALL addr16
#########################################################

import __util as u
import random
from __asmconst import *
from __numutil import numutil as ntl

p = u.create_test()


def creat_jump_link(jmpords, seg_str_list):
    for i in range(len(jmpords)):
        seg_no = jmpords[i]
        s = f'JMP_SEG_{seg_no}:'

        if i < len(jmpords) - 1:
            next_seg_no = jmpords[i + 1]
            s += f'''
            LCALL JMP_SEG_{next_seg_no}
            '''

        s += f'''
        RET
        {atl.crash()}
        '''
        
        seg_str_list[seg_no] = s

def sample_random(a, l):
    start = 0
    while start < l and start < len(a):
        idx = random.randint(start,len(a) - 1)
        temp = a[idx]
        a[idx] = a[start]
        a[start] = temp
        start += 1
    return a[0:l],a[l:]

total_time = 9113
call_per_time = 64
a = list(range(total_time))
seg_str_list = list(range(total_time))

s = ''
while len(a):
    jmpords, a = sample_random(a, call_per_time)
    s  += f'''
            MOV SP, #0xFF
            LCALL JMP_SEG_{jmpords[0]}
        '''
    creat_jump_link(jmpords, seg_str_list)


p += s
p += "LJMP TEST_END"
p += '\n'.join(seg_str_list)
p += "TEST_END:"