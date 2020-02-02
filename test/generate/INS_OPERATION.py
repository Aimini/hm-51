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



def op_a_addc_xx(ram, B, use_psw_cy):
    if use_psw_cy:
        ci = ram.get_bit(SFR_PSW.x, 7)
    else:
        ci = 0
    A = ram.get_direct(SFR_A.x)

    SL = (A & 0xF) + (B & 0xF) + ci
    S = A + B + ci

    cy = 1 if S > 0xFF else 0
    ram.set_bit(SFR_PSW.x, 7, cy)

    ac = 1 if SL > 0xF else 0
    ram.set_bit(SFR_PSW.x, 6, ac)

    ov = 1 if((~(A ^ B)) & (A ^ S)) & 0x80 else 0
    ram.set_bit(SFR_PSW.x, 2, ov)

    ram.set_direct(SFR_A.x, S & 0xFF)


def op_a_subb_xx(ram, B):
    A = ram.get_direct(SFR_A.x)
    ci = ram.get_bit(SFR_PSW.x, 7)

    SL = (A & 0xF) - (B & 0xF) - ci
    S = A - B - ci

    cy = 1 if S < 0 else 0
    ram.set_bit(SFR_PSW.x, 7, cy)

    ac = 1 if SL < 0 else 0
    ram.set_bit(SFR_PSW.x, 6, ac)

    ov = 1 if((A ^ B) & (A ^ S)) & 0x80 else 0
    ram.set_bit(SFR_PSW.x, 2, ov)

    ram.set_direct(SFR_A.x, S & 0xFF)