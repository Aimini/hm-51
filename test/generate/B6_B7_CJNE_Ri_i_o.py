#########################################################
# 2020-01-29 08:48:31
# AI
# ins: CJNE  @Ri, #immed, offset
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
    
    p += f"""
    SJMP JMP_SEG_{order}_{jmpords[0]}
    """
    seg_str_list = list(range(jump_count))
    ris = list(p.rdirect())

    for i in range(len(jmpords)):
        rs = random.randrange(4)
        ri = random.randrange(2)
        psw_rs = rs << 3
        RI = atl.RI(rs, ri)
        indirect = random.getrandbits(8)
        value = random.getrandbits(8)
        immed = random.getrandbits(8)
        
        seg_no = jmpords[i]
        s = f'''
        JMP_SEG_{order}_{seg_no}:
        MOV PSW, {atl.I(psw_rs)}
        MOV {atl.D(RI.addr)}, {atl.I(indirect)}
        MOV {RI}, {atl.I(value)}
        '''
        ram.set_direct(SFR_PSW.x, psw_rs)
        ram.set_direct(RI.addr, indirect)
        ram.set_iram(indirect, value)
        
        
        if i == len(jmpords) - 1:
            target = f"JMP_SEG_END_{order}"
        else:
            target = f"JMP_SEG_{order}_{jmpords[i + 1]}"

        
        
        if ram.get_iram(ram.get_iram(RI.addr)) != immed:
            s += f'''
            CJNE {RI},{atl.I(immed)}, {target}
            {atl.crash()}
            '''
        else:
            jump_wrong = f"SEG_WRONG_{order}_{seg_no}"
            s += f'''
            CJNE {RI},{atl.I(immed)}, {jump_wrong}
            SJMP {target}
            {jump_wrong}:
            {atl.crash()}
            '''

        seg_str_list[i] = s


    p += '\n'.join(seg_str_list)
    p += f"JMP_SEG_END_{order}:"

for x in range(635):
    creat_jump_link(p, 7, x)
    p += atl.dump()

