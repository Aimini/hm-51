import sys
import argparse
##
## AI
## generate UART reciver state machine LUT


def enum_input(callback):
    '''
     To enumerate all the numbers x in [0 ~ 2 ^ 13) x.
     treat x as a binary number, 
     then state = x[3:0](4-bit), counter = x[7:4](4-bit),
    sample_bits = x[10:8](3-bit), sample_enable = x[11](1-bit) 
    rx_enalbe = x[12](1-bit)  
     invoke callback(ci,f,b, a) to generate  low part output
    '''
    for head_bit in range(2**1):
        for _sbuf_le in range(2**1):
            for sample_it in range(2**1):
                for next_frame in range(2**1):
                    for state_reg in range(2**4):
                            callback(head_bit, _sbuf_le,sample_it,next_frame,state_reg)


S_PRE = 0
S_WAIT_SAMPLE = 1# wait to sync with sample_it signal
S_SBIT = 6
S_D0 = 7
S_D1 = 8
S_D2 = 9
S_D3 = 10
S_D4 = 11
S_D5 = 12
S_D6 = 13
S_D7 = 14
S_DEND = 15 # must be 15 bcz hardware using it to generate TX_END signal
def gen(head_bit,_sbuf_le,sample_it,next_frame,state_reg):
    cnt_bin_str = bin(state_reg)[2:].zfill(4)
    s = int(cnt_bin_str[::-1],2)

    next_state = s
    s0 = 0
    s1 = 0
    tx_ing = 0
    TX = 1

    if s == S_SBIT:
        tx_ing = 1
        TX = 0 #start_bit
    elif S_D0 <= s and s <= S_D7:
        tx_ing = 1
        TX = head_bit
    elif s == S_DEND:
        tx_ing = 1
        TX = 1

    if _sbuf_le == 0:
        s0 = 1
        s1 = 1
        # load data and
        if sample_it:
            next_state = S_SBIT
        else:
            next_state = S_WAIT_SAMPLE
    else:
        if s == S_WAIT_SAMPLE:
            if sample_it:
                next_state = S_SBIT
        if next_frame:
            next_state = s + 1
            if S_D0<= s <=S_DEND:
                s1 = 1
        

    return next_state | (s0 << 4) | (s1 << 5) | (tx_ing << 6) | (TX << 7)


def gen_to_file(fname):
    d = bytearray()

    def write_one_byte(re, se, sbs, cnt, s):
        d.append(gen(re, se, sbs, cnt, s) & 0xFF)

    enum_input(write_one_byte)

    with open(fname, 'wb') as f:
        f.write(d)


usage = """
usage:
    receiver.py <output_file>
"""

if len(sys.argv) < 2:
    print(usage)
else:
    fname = sys.argv[1]
    gen_to_file(fname)
