#########################################################
# 2020-01-29 08:15:39
# AI
# ins: CJNE  A, #immed, offset
#########################################################
import __util as u
import random
import itertools
from __asmconst import *
from __numutil import numutil as ntl
from __51util import SIMRAM
p = u.create_test()
ram = SIMRAM()



def creat_jump_link(p, jump_count, order):
    jmpords = list(range(jump_count))
    random.shuffle(jmpords)

    p += f"""
    SJMP JMP_SEG_{order}_{jmpords[0]}
    """
    seg_str_list = list(range(jump_count))

    for i in range(len(jmpords)):
        a = random.getrandbits(8)
        immed = random.getrandbits(8)
        
        seg_no = jmpords[i]
        s = f'''
        JMP_SEG_{order}_{seg_no}:
        MOV ACC, {atl.I(a)}
        '''
        
        if i == len(jmpords) - 1:
            target = f"JMP_SEG_END_{order}"
        else:
            target = f"JMP_SEG_{order}_{jmpords[i + 1]}"

        
        
        if a !=immed:
            s += f'''
            CJNE A, {atl.I(immed)}, {target}
            {atl.crash()}
            '''
        else:
            jump_wrong = f"SEG_WRONG_{order}_{seg_no}"
            s += f'''
            CJNE A, {atl.I(immed)}, {jump_wrong}
            SJMP {target}
            {jump_wrong}:
            {atl.crash()}
            '''

        seg_str_list[i] = s


    p += '\n'.join(seg_str_list)
    p += f"JMP_SEG_END_{order}:"

for x in range(800):
    creat_jump_link(p, 8, x)

    p += atl.dump()

