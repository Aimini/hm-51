import sys
import argparse
##
## 2019-12-18 23:10:18
## AI
## genrate double operands ALU LUT(some function using A only)
## AT28C64 chips have 13bit input, 8 bit ouput, for
## support 8 + 8 = 16 bit input, I split it's to two 4-bit part, low and high
## 1 bit for fi(flag in), 4bit for operand A nibble, 4bit for operaend B nibble and 4bit for function select
## high -> low
## fi | f[3:0] | b[3:0] | a[3:0]
# for ouput, we using treat it as two 4-bit ouput. For function that must send info
# to high part alu(ADDC, SUBB, etc.), we using high nibble are used to send flag 
# like carry or ov, oterwise we using high nibble to encode another function.
## high -> low
#  QH[3:0] | QL[3:0]
## becuase low part and high part have different operation on dirrent function, so
## we must generate diffrent LUT for low part and high part.
# for example :
#    EXTB A,B, extract bit filed A[B] to Q[7] ,Q[6:0] are always 0.
#   for low part,
#   bus ouput(Q[3:0]) is always zero, and co(Q[7]) is extracted bit from lower part,
#　 if B < 4, co is A[B], otherwise, co is zero.
#   for high part,
#   Q[2:0] is zero, if B < 4, co is A[B], Q[3] take the value from low part's co.
#   otherwise, Q[3] = A[B]


def enum_input(callback):
    '''
     To enumerate all the numbers x in [0 ~ 2 ^ 13) x.
     treat x as a binary number, 
     then a = x[3:0](4-bit), b = x[7:4](4-bit), f = x[11:8](4-bit), ci = x[12](1-bit)   
     invoke callback(ci,f,b, a) to generate  low part ouput
    '''
    for ci in range(2**1):
        for f in range(2**4):
            for b in range(2**4):
                for a in range(2**4):
                    callback(ci, f, b, a)


def get_flag_add(a, b, ci):
    R = a + b + ci
    cy = (R >> 1) & 0x08                    # carry at bit 3
    # (A XNOR B) AND (A XOR R)
    ov = (((~(a ^ b)) & (a ^ R)) >> 1) & 0x04  # ov at bit 2
    return cy | ov , (R & 0xF)


def get_flag_sub(a, b, ci):
    R = a - b - ci
    cy = 1 if R < 0 else 0
    cy <<= 3
    R = R & 0x0F
    # (A NOR B) AND (A NOR R)
    ov = (((a ^ b) & (a ^ R)) >> 1) & 0x4
    return cy | ov , R


def generate_low_by_op(ci, f,  b, a):
    RL = 0
    RH = 0

    if f == 0x0:# XOR
        RL = a ^ b

    elif f == 0x1:# DA/DAF
        # DA low part, assume AC flag in B[3], if B[3] == 1 ,then add 6 to A[3:0]
        if (b & 0x8) or a > 9:
            RH,RL = get_flag_add(a, 6, 0)
        else:
            RH,RL = 0, a # Rn IR, PSW

    elif f == 0x2:  # ADDC/ADDCF
        RH,RL = get_flag_add(a,b,ci)

    elif f == 0x3: # SUBB/SUBBF
        RH,RL = get_flag_sub(a,b,ci)

    elif f == 0x4:  #A/PF
        RL = a
        T = '{:b}'.format(a).count('1')
        RH = 8 if (T & 1) else 0 # pass pf to high part

    elif f == 0x5: # B/ZF
        RL = b
        RH = 8 if a == 0 else 0 # send ZF to high part

    elif f == 0x6: #0/INSB

        # INSB A,B (BIDX)
        # insert ci to A[B]
        # in low part we just care of A in range [3:0],
        # and don't for get transport ci to high part(copy ci to co)
        bidx = a
        value = b
        shift = bidx & 0x7
        if bidx < 4:
            RH = (value & (~(0x1 << shift))) | (ci << shift)
        else:
            RH = value
    elif f == 0x7: # AND/EXTB
        RL = a & b
        # EXTB A,B(BIDX)
        # extract BIT ,BIT =  A[B], BIT at Q[7]
        #
        # for example A = 0110 1001
        # if B = 0, Q = 1 000 0000, CO = 1
        # if B = 1, Q = 0 000 0000, CO = 0
        # if B = 3, Q = 1 000 0000, CO = 1
        # in low part we just care of A in range [3:0],
        # and beacause of ouput bit is in Q[7], we must send extracted bit
        # to high part by using co.
        bidx = a
        value = b
        shift = bidx & 0x7
        if shift  < 4:
            co = (value >> shift) & 1
        else:
            co = 0
        RH = co << 3

    elif f == 0x8: # IRQN2IRQ
        # IRQN2IRQ A
        # 2-4 line decoder, if A[3](valid flag) is 0, the ouput is 0
        if a & 0x8:
            RL = 1 << (a & 0x3)
        else:
            RL = 0

    elif f == 0x9: # SETPSWF A (PSW),B
        # just replace A's OV AC CY from B
        # for lower part, set OV only
        RL = (0xb & a) | ((~0xb) & (b >> 1))

    elif f == 0xA:# ADDR11REPLACE A, B
        # asume A = PCH[3:0], B = IR[7:4]
        # according to instruction set manual, we have PC[10:8] = IR[7:5]
        # namely, A[2:0] = B[3:1]
        RL = (a & 0xE) | ((b) >> 1)

    elif f == 0xB:  # SHIRQN A(ISR or IRQ),B(IP)
        # from interrupt aspect, A is IRQ, B = IP,
        # to get IRQ then have IP mask, we get PIRQ = A & B
        # the IRQ with IP also have higher priority than IRQ without IP,
        # if we make 0 - 3 to encode IRQ0-3, 4-7 to enocode IRQ0-3 with IP
        # after unsing 8-3 encoder, we can treat Q[2] as IP flag, Q[1:0] as IRQ number.
        RL = a | ((a & b) << 4)
        valid = 1 if RL > 0 else 0
        RL = 7 - '{:b}'.format(RL).find('1')
        RL = (valid << 3) | RL  

    elif f == 0xC:
        RL = (a & 0x1) | (b & 0x8) # Ri IR, PSW
        RH = a | b #OR
    elif f == 0xD: 
        RL = (a & 0x7) | (b & 0x8) # Rn IR, PSW
        RH = a & b #AND

    elif f == 0xE: # NA/ SETPF
        RL = ~a
        RH = (a & 0xE) | ci
    elif f == 0xF: #INCC
        RH,RL = get_flag_add(a,0,ci)

    v =  ((RH & 0xF) << 4) | (RL& 0xF)
    return v


def generate_high_by_op(ci, f, b, a):
    RL = 0
    RH = 0
    if f == 0x0:  #XOR
        RL = a^b

    elif f == 0x1:  # DA/DAF
        # DA low part, assume CY flag in B[3], if B[3] == 1 ,then add 6 to A
        # don't forget cy from low part
        T = a + ci
        if (b & 0x8) or T > 9:
            RH,RL = get_flag_add(T, 6, 0)

    elif f == 0x2:  #ADDC/ADDCF
        RH,RL = get_flag_add(a, b, ci)

    elif f == 0x3:  # SUBB/SUBBF
        RH,RL = get_flag_sub(a, b, ci)

    elif f == 0x4:  # A/PF
        RL = a
        # PF A
        T = '{:b}'.format(a).count('1')
        T = T % 2 == 1
        if (ci and not T) or (not ci and T):
            RH = 8
        else:
            RH = 0

    elif f == 0x5:  # B/ZF
        RL = b
        T = ci == 1 and a == 0
        RH = 8 if T else 0

    elif f == 0x6:  #OR/INSB
        RL = a | b
        # INSB A,B (BIDX)
        # insert ci to A[B]
        # in low part we just care of A in range [3:0],
        # and don't forget transport ci to high part(copy ci to co)
        bidx = a
        value = b
        shift = bidx & 0x7
        if shift < 4:
            RH = value
        else:
            T = shift & 0x3
            RH = (value & (~(0x1 << T))) | (ci << T)

    elif f == 0x7:  #0/EXTB
        # EXTB A,B(BIDX)
        # extract BIT ,BIT =  A[B], BIT at Q[7] and co
        bidx = a
        value = b
        shift = bidx & 0x7
        if shift < 4:
            co = ci
        else:
            co = value >> (shift & 0x3)
        co &= 1
        RH = (co << 3)
    
    elif f == 0x8:  # IRQN2IRQ
        # all ouput are in low part
        RL = 0

    elif f == 0x9: # SETPSWF
        # SETPSWF A (PSW),B
        # just replace A's OV AC CY from B
        # for high part, set AC and CY
        RL = (0x3 & a) | (0xC & b)

    elif f == 0xA: # ADDR11REPLACE
        # ADDR11REPLACE A (PCH), B(SWAPED IR)
        # don't care in high part
        RL = a

    elif f == 0xB:  # SHIRQN A(ISR or IRQ),B(IP)
        # all Louput are in low part
        RL = 0

    elif f == 0xC: # Rn IR, PSW/OR
        RL = b & 0x1 # RS1
        RH = a | b
    elif f == 0xD:  # Ri IR, PSW/AND
        RL = b & 0x1 #RS1
        RH = a & b
    elif f == 0xE:  #NA / SETPF
        RL =  ~a
        RH = a
    elif f == 0xF: #INCC
        RH,RL = get_flag_add(a,0,ci)
    v =  ((RH & 0xF) << 4) | (RL& 0xF)
    return v


def gen_to_file(lowfilepath,highfilepath):
    l = bytearray()
    h = bytearray()

    def write_one_byte(ci, f, b, a):
        l.append(generate_low_by_op(ci, f, b, a) & 0xFF)
        h.append(generate_high_by_op(ci, f, b, a) & 0xFF)
    enum_input(write_one_byte)

    with open(lowfilepath, 'wb') as f:
        f.write(l)

    with open(highfilepath, 'wb') as f:
        f.write(h)

arg_parser =  argparse.ArgumentParser(description='generate two operands ALU LUT low part and high part')

arg_parser.add_argument('--low-output',  action='store', type=str, dest='low',  default='alud-low.bin')
arg_parser.add_argument('--high-output', action='store', type=str, dest='high', default='alud-high.bin')
op = arg_parser.parse_args(sys.argv[1:])
gen_to_file(op.low,op.high)