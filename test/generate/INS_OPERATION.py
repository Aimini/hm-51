#########################################################
# 
# for(int i = 0;i  < iter_test_time; ++i )
# {
#   fill ram to all rn;
#   for(int rs = 0;rs < 4; ++rs)
#   {
#       set rs in PSW;
#       set A to A_inital_value;
#       for(int rn = 0; rn < 8; ++ rn)
#       {
#           do opeartion with A and RN;
#           check result in A;
#       }
#   }
# }
#########################################################
from __asmconst import *

def op_anl(a0, a1, ram):
    return a0 & a1

def op_orl(a0, a1, ram):
    return a0 | a1

def op_xrl(a0,a1, ram):
    return a0 ^ a1

def op_addc_xx(a0, a1, ram, use_psw_cy):
    if use_psw_cy:
        ci = ram.get_bit(SFR_PSW.x, 7)
    else:
        ci = 0

    SL = (a0 & 0xF) + (a1 & 0xF) + ci
    S = a0 + a1 + ci

    cy = 1 if S > 0xFF else 0
    ram.set_bit(SFR_PSW.x, 7, cy)

    ac = 1 if SL > 0xF else 0
    ram.set_bit(SFR_PSW.x, 6, ac)

    ov = 1 if((~(a0 ^ a1)) & (a0 ^ S)) & 0x80 else 0
    ram.set_bit(SFR_PSW.x, 2, ov)

    return S & 0xFF

def op_addc(a0, a1, ram):
    return op_addc_xx(a0,a1,ram, True)

def op_add(a0, a1, ram):
    return op_addc_xx(a0,a1,ram, False)

def op_subb(a0, a1, ram):
    ci = ram.get_bit(SFR_PSW.x, 7)

    SL = (a0 & 0xF) - (a1 & 0xF) - ci
    S = a0 - a1 - ci

    cy = 1 if S < 0 else 0
    ram.set_bit(SFR_PSW.x, 7, cy)

    ac = 1 if SL < 0 else 0
    ram.set_bit(SFR_PSW.x, 6, ac)

    ov = 1 if((a0 ^ a1) & (a0 ^ S)) & 0x80 else 0
    ram.set_bit(SFR_PSW.x, 2, ov)

    return S & 0xFF

def op_mov(a0, a1, ram):
    return a1

def op_a_addc_xx(ram, B, use_psw_cy):
    A = ram.get_direct(SFR_A.x)
    S = op_addc_xx(A,B,ram,use_psw_cy)
    ram.set_direct(SFR_A.x, S)


def op_a_subb_xx(ram, B):
    A = ram.get_direct(SFR_A.x)
    S = op_subb(A, B, ram)
    ram.set_direct(SFR_A.x, S)


OP_LUT = {
    "ADD" : op_add,
    "ADDC": op_addc,
    "ORL" : op_orl,
    "ANL" : op_anl,
    "XRL" : op_xrl,
    "SUBB": op_subb,
    "MOV" : op_mov,
}