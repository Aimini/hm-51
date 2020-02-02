#########################################################
# 2020-01-28 19:29:22
# AI
# ins: DJNZ direct, offset
#########################################################

import __util as u
import random
import itertools
from __asmconst import *
from __numutil import numutil as ntl
from __51util import SIMRAM
p = u.create_test()
ram = SIMRAM()


def init_rs(rs, psw_rs, p):
    


def init_rn(RN, p):
    value = random.getrandbits(8)
    p += atl.move(atl.D(RN.addr), atl.I(value))
    ram[RN.addr] = value
    

def creat_jump_link(p, jump_count, order):
    jmpords = list(range(jump_count))
    random.shuffle(jmpords)

    p += f"""
    SJMP JMP_SEG_{order}_{jmpords[0]}
    """
    seg_str_list = list(range(jump_count))

    for i in range(len(jmpords)):
        rs = random.randrange(4)
        rn = random.randrange(8)
        RN = atl.RN(rs, rn)

        value = ram[RN.addr] - 1
        ram[RN.addr] = value
        
        seg_no = jmpords[i]
        s = f'''
        JMP_SEG_{order}_{seg_no}:
        MOV PSW, {atl.I(rs << 3)}
        '''
        
        
        if i == len(jmpords) - 1:
            target = f"JMP_SEG_END_{order}"
        else:
            target = f"JMP_SEG_{order}_{jmpords[i + 1]}"

        if value != 0:
            s += f'''
            DJNZ {RN}, {target}
            {atl.crash()}
            '''
        else:
            jump_wrong = f"SEG_WRONG_{order}_{seg_no}"
            s += f'''
            DJNZ {RN}, {jump_wrong}
            SJMP {target}
            {jump_wrong}:
            {atl.crash()}
            '''

        seg_str_list[i] = s


    p += '\n'.join(seg_str_list)
    p += f"JMP_SEG_END_{order}:"

for x in range(256):
    p.iter_rn(init_rs, init_rn)
    creat_jump_link(p, 8, x)
