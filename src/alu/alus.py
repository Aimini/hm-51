import sys
import optparse
##
## 2019-12-18 22:52:07
## AI
## genrate signal operand ALU LUT
## because I have lot of AT28C64 chips
## so I get 13bit LUT
## 1 bit for ci, 8 bit for operand A, and 4bit for function select
## high -> low
## ci | f | a
## document: src/alu/README.md

SFR_MAP = {
    0x81:0,#"SP"],
    0x82:1,#"DPL"],
    0x83:2,#"DPH"],
    0xA8:3,#"IE"],
    0xB8:4,#"IP"],
    0xD0:5,#"PSW"],
    0xE0:6,#"A"],
    0xF0:7,#"B"],
}

def enum_input(callback):
    """
     To enumerate all the numbers x in [0 ~ 2 ^ 13) x.
     treat x as a binary number, 
     then ci = x [0](1-bit), a = x [8:1](8-bit), f = [12:9](4-bit)   
     invoke callback(ci,f,a) to generate ouput
    """
    for ci in range(2**1):
        for f in range(2**4):
            for a in range(2**8):
                callback(ci, f, a)


def generate_by_op(ci, f, A):
    R = 0
    if f == 0x0:  # ADJF
        R = (A & 0xB7) | ((A & 0x08) << 3) | ((A & 0x40) >>3)
    elif f == 0x1: #IVADDR
        # don't forget remove useless flag
        IRNQ = A & 0x7
        R = (IRNQ << 3) + 3
    elif f == 0x2: #CAA
        if ci == 0:
            R = A

    elif f == 0x3:  # SFR
        T = SFR_MAP.get(A)
        
        if T is not None:
            if T > 0x7:
                raise Exception('SFR index must less than 8')
            R = T | 0x8

    elif f == 0x4:  # RR A
        R = ((A & 1) << 7) | (A >> 1)
    elif f == 0x5:  # RL A
        R = ((A & 0x80) >> 7) | (A << 1)
    elif f == 0x6:  # RRC A
        R = (A >> 1) | (ci << 7)
    elif f == 0x7:  # RLC A
        R = (A << 1) | (ci)
    elif f == 0x8:  # INC A
        R = A + 1
    elif f == 0x9:  # DEC A
        R = A - 1
    elif f == 0xA:  # BADDR A
        if A < 0x80:
            R = 0x20 + (A >> 3)
        else:
            R = A & 0xF8
    elif f == 0xB:  # BIDX  A
        # get bit index from address and store it in both of A[7:4] and A[3:0]
        T = A & 0x7
        R = T | (T << 4)
    elif f == 0xC:  # SETCY A
        R = (A & 0x7F) | (ci << 7)
    elif f == 0xD:  # SELHIRRQN
        IP_L = (A & 4) >> 2
        IV_L = (A & 8) >> 3
        IR_L = (A & 3)

        IP_H = ((A >> 4) & 4) >> 2
        IV_H = ((A >> 4) & 8) >> 3
        IR_H = ((A >> 4) & 3)
        if IV_L:
            if IV_H and IP_H and not IP_L:
                R = (IR_H + 4) | (IP_H << 7)
            else:
                R = (IR_L) | (IP_L << 7)
        else:
            if IV_H:
                R = (IR_H + 4) | (IP_H << 7)

    elif f == 0xE:  # ISRRET ISR
        if A & 0x40:
            R = A & 0xBF
        else:
            R = A & 0xDF
    elif f == 0xF:  # SWAP
        R = (A >> 4) | (A << 4)

    return R & 0xFF


def gen_to_file(filepath):
    a = bytearray()

    def write_one_byte(ci, f, A):
        a.append(generate_by_op(ci, f, A) & 0xFF)
    enum_input(write_one_byte)
    with open(filepath, "wb") as f:
        f.write(a)


arg_parser = optparse.OptionParser()
arg_parser.add_option('-o', '--output', action='store', type="string", dest='output', default='alus.bin')
op, ar = arg_parser.parse_args(sys.argv[1:])
gen_to_file(op.output)

