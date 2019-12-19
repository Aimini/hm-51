import sys
import argparse
##
## 2019-12-18 23:10:18
## AI
## genrate double operands ALU LUT(some function using A only)
## AT28C64 chips have 13bit input, 8 bit ouput, for
## support 8 + 8 = 16 bit input, I split it's to two 4-bit part, low and high
## 1 bit for ci, 4bit for operand A nibble, 4bit for operaend B nibble and 4bit for function select
## high -> low
## ci | f[3:0] | b[3:0] | a[3:0]
# for ouput, we only using 4-bit connect to data bus, high nibble are used to send flag like carry or ov.
## high -> low
## |co |ov| 0| 0 | Q[3:0]
## becuase low part and high part have different operation on dirrent function, so
## we must generate diffrent LUT for low and high part.
# for example :
#    EXTB A,B, extract bit filed A[B] to Q[7] ,Q[6:0] are always 0.
#   for low part,
#   bus ouput(Q[3:0]) is always zero, and co(Q[7]) is extracted bit from lower part,
#　 if B < 4, co is A[B], otherwise, co is zero.
#   for high part,
#   Q[2:0] is zero, if B < 4, co is A[B], Q[3] take the value from low part's co.
#   otherwise, Q[3] = A[B]


def enum_input(callback):
    """
     To enumerate all the numbers x in [0 ~ 2 ^ 13) x.
     treat x as a binary number, 
     then a = x[3:0](4-bit), b = x[7:4](4-bit), f = x[11:8](4-bit), ci = x[12](1-bit)   
     invoke callback(ci,f,b, a) to generate  low part ouput
    """
    for ci in range(2**1):
        for f in range(2**4):
            for b in range(2**4):
                for a in range(2**4):
                    callback(ci, f, b, a)


def get_flag_add(a, b, ci):
    R = a + b + ci
    cy = (R << 3) & 0x80                     # carry at bit 7
    # (A XNOR B) AND (A XOR R)
    ov = (((~(a ^ b)) & (a ^ R)) << 3) & 0x40  # ov at bit 6
    return cy | ov | (R & 0xF)


def get_flag_sub(a, b, ci):
    R = a - b - ci
    cy = 1 if R < 0 else 0
    cy <<= 7
    R = R & 0x0F
    # (A NOR B) AND (A NOR R)
    ov = (((a ^ b) & (a ^ R)) << 3) & 0x40
    return cy | ov | R


def generate_low_by_op(ci, f,  b, a):
    R = 0
    if f == 0x0:  # A AND B (PF)
        R = a | b

    elif f == 0x1:  # A OR B (ZF)
        R = a & b

    elif f == 0x2:  # A XOR B
        R = a ^ b
    elif f == 0x3:  # B
        R = b
    elif f == 0x4:  # A + B
        R = get_flag_add(a, b, 0)
    elif f == 0x5:  # A + B + CI
        R = get_flag_add(a, b, ci)
    elif f == 0x6:  # A - B - CI
        R = get_flag_sub(a, b, ci)
    elif f == 0x7:  # DA
        # DA low part, assume AC flag in B[3], if B[3] == 1 ,then add 6 to A[3:0]
        if (b & 0x8) or a > 9:
            R = get_flag_add(a, 6, 0)
        else:
            R = a
    elif f == 0x8:  # SHIRQN A(ISR or IRQ),B(IP)
        # from interrupt aspect, A is IRQ, B = IP,
        # to get IRQ then have IP mask, we get PIRQ = A & B
        # the IRQ with IP also have higher priority than IRQ without IP,
        # if we make 0 - 3 to encode IRQ0-3, 4-7 to enocode IRQ0-3 with IP
        # after unsing 8-3 encoder, we can treat Q[2] as IP flag, Q[1:0] as IRQ number.
        R = (a | (a & b) << 4)
        valid = 1 if R > 0 else 0
        R = 7 - "{:b}".format(R).find('1')
        R = (valid << 3) | R
    elif f == 0x9:  # IRQN2IRQ A
        # 2-4 line decoder, if A[3](valid flag) is 0, the ouput is 0
        if a & 0x8:
            R = 1 << (a & 0x3)
        else:
            R = 0

    elif f == 0xA:  # EXTB A,B(BIDX)
        # extract BIT ,BIT =  A[B], BIT at Q[7]
        #
        # for example A = 0110 1001
        # if B = 0, Q = 1 000 0000, CO = 1
        # if B = 1, Q = 0 000 0000, CO = 0
        # if B = 3, Q = 1 000 0000, CO = 1
        # in low part we just care of A in range [3:0],
        # and beacause of ouput bit is in Q[7], we must send extracted bit
        # to high part by using co.
        if b < 4:
            co = (a >> b) & 1
        else:
            co = 0
        R = co << 7

    elif f == 0xB:  # INSB A,B (BIDX)
        # insert ci to A[B]
        # in low part we just care of A in range [3:0],
        # and don't for get transport ci to high part(copy ci to co)
        if b < 4:
            R = (a & (~(0x1 << b))) | (ci << b)
        else:
            R = a

    elif f == 0xC:  # ADDR11REPLACE A (PCH), B(SWAPED IR)
        # asume A = PCH[3:0], B = IR[7:4]
        # according to instruction set manual, we have PC[10:8] = IR[7:5]
        # namely, A[2:0] = B[3:1]
        R = (a & 0xE) | ((b) >> 1)

    elif f == 0xD:  # SETPSWF A (PSW),B
        # just replace A's OV AC CY from B
        # for lower part, set OV only
        R = (0xb & a) | ((~0xb) & b)

    elif f == 0xE:  # Rn IR, PSW
        R = (a & 0x7) & (b & 0x80)
    elif f == 0xF:  # Ri IR, PSW
        R = (a & 0x1) & (b & 0x80)

    return R & 0xF


def generate_high_by_op(ci, f, b, a):
    R = 0
    if f == 0x0:  # A AND B (PF)
        R = a | b

    elif f == 0x1:  # A OR B (ZF)
        R = a & b

    elif f == 0x2:  # A XOR B
        R = a ^ b

    elif f == 0x3:  # B
        R = b

    elif f == 0x4:  # A + B
        # low part must take ci from low part
        R = get_flag_add(a, b, ci)

    elif f == 0x5:  # A + B + CI
        R = get_flag_add(a, b, ci)

    elif f == 0x6:  # A - B - CI
        R = get_flag_sub(a, b, ci)

    elif f == 0x7:  # DA
        # DA low part, assume CY flag in B[0], if B[0] == 1 ,then add 6 to A
        # don't forget cy from low part
        R = a + 1
        if (b & 0x1) or R > 9:
            R = get_flag_add(a, 6, 0)
        else:
            R = a

    elif f == 0x8:  # SHIRQN A(ISR or IRQ),B(IP)
        # all ouput are in low part
        R = 0
    elif f == 0x9:  # IRQN2IRQ A
        # all ouput are in low part
        R = 0

    elif f == 0xA:  # EXTB A,B(BIDX)
        # extract BIT ,BIT =  A[B], BIT at Q[7] and co
        if b < 4:
            q = ci
        else:
            q = (a >> (b & 0x3) & 1)
        R = (q << 4) | (q << 8)

    elif f == 0xB:  # INSB A,B (BIDX)
        # insert ci to A[B]
        # in low part we just care of A in range [3:0],
        # and don't forget transport ci to high part(copy ci to co)
        if ci < 4:
            R = a
        else:
            R = b & 0x3
            R = (a & (~(0x1 << R))) | (ci << R)

    elif f == 0xC:  # ADDR11REPLACE A (PCH), B(SWAPED IR)
        # don't care in high part
        R = 0

    elif f == 0xD:  # SETPSWF A (PSW),B
        # just replace A's OV AC CY from B
        # for high part, set AC and CY
        R = (0x3 & a) | (0xC & b)

    elif f == 0xE:  # Rn IR, PSW
        R = b & 0x1 # RS1
    elif f == 0xF:  # Ri IR, PSW
        R = b & 0x1 #RS1

    return R & 0xF


def gen_to_file(lowfilepath,highfilepath):
    l = bytearray()
    h = bytearray()

    def write_one_byte(ci, f, b, a):
        l.append(generate_low_by_op(ci, f, b, a) & 0xF)
        h.append(generate_high_by_op(ci, f, b, a) & 0xF)
    enum_input(write_one_byte)

    with open(lowfilepath, "wb") as f:
        f.write(h)

    with open(highfilepath, "wb") as f:
        f.write(h)

arg_parser =  argparse.ArgumentParser(description='generate two operands ALU LUT low part and high part')

arg_parser.add_argument('--low-output',  action='store', type=str, dest='low',  default='alud-low.bin')
arg_parser.add_argument('--high-output', action='store', type=str, dest='high', default='alud-high.bin')
op = arg_parser.parse_args(sys.argv[1:])
gen_to_file(op.low,op.high)