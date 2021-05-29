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
        for _fifo_ef in range(2**1):
            for sample_it in range(2**1):
                for next_frame in range(2**1):
                    for state_reg in range(2**4):
                            callback(head_bit, _fifo_ef,sample_it,next_frame,state_reg)


S_IDLE = 0
S_D = [1 + (x << 1) for x in range(0,8)]
S_SBIT = 2
S_DEND = 4

ALL_STATE = [S_IDLE, S_SBIT, *S_D, S_DEND]

def gen(head_bit,_fifo_ef,sample_it,next_frame,state_reg):
    cnt_bin_str = bin(state_reg)[2:].zfill(4)
    s = int(cnt_bin_str[::-1],2)

    next_state = s
    _fifo_ren = 1
    tx_ing = 0
    TX = 1
    
    if s not in ALL_STATE:
        next_state = S_IDLE
    else:
        ## generate tx_ing and TX
        if s == S_SBIT:
            tx_ing = 1
            TX = 0 #start_bit
        elif s in S_D:
            tx_ing = 1
            TX = head_bit
        elif s == S_DEND:
            tx_ing = 1
            TX = 1

        if (s  == S_IDLE and sample_it) or  (s == S_DEND and next_frame):
            if _fifo_ef == 1:
                _fifo_ren = 0
                # load data and
                next_state = S_SBIT
            else:
                next_state = S_IDLE
        else:
            if next_frame:
                next_state = ALL_STATE[(ALL_STATE.index(s) + 1) % len(ALL_STATE)]
                
        

    return next_state | (_fifo_ren << 4) | (tx_ing << 5) | (TX << 6)


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
