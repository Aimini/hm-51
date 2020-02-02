#########################################################
# 2020-01-28 21:23:05
# AI
# ins: CJNE  A, direct, offset
#########################################################
import __util as u
import random
import itertools
from __asmconst import *
from __numutil import numutil as ntl
from __51util import SIMRAM
p = u.create_test()
ram = SIMRAM()


def init_ram(addr, p):
    value = random.randrange(8)
    p += atl.move(atl.D(addr), atl.I(value))
    ram.set_direct(addr, value)
    

def creat_jump_link(p, jump_count, order):
    jmpords = list(range(jump_count))
    random.shuffle(jmpords)

    p += f"""
    SJMP JMP_SEG_{order}_{jmpords[0]}
    """
    seg_str_list = list(range(jump_count))
    ris = list(p.ris())

    for i in range(len(jmpords)):
        a = random.getrandbits(8)
        addr = random.choice(ris)
        
        seg_no = jmpords[i]
        s = f'''
        JMP_SEG_{order}_{seg_no}:
        MOV ACC, {atl.I(a)}
        '''
        ram.set_direct(SFR_A.x, a)
        
        if i == len(jmpords) - 1:
            target = f"JMP_SEG_END_{order}"
        else:
            target = f"JMP_SEG_{order}_{jmpords[i + 1]}"

        
        
        if a != ram.get_direct(addr):
            s += f'''
            CJNE A, {atl.D(addr)}, {target}
            {atl.crash()}
            '''
        else:
            jump_wrong = f"SEG_WRONG_{order}_{seg_no}"
            s += f'''
            CJNE A, {atl.D(addr)}, {jump_wrong}
            SJMP {target}
            {jump_wrong}:
            {atl.crash()}
            '''

        seg_str_list[i] = s


    p += '\n'.join(seg_str_list)
    p += f"JMP_SEG_END_{order}:"

for x in range(128):
    p.iter_is(init_ram)
    creat_jump_link(p, 8, x)
    p += atl.dump()

