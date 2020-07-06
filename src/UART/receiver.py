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
     invoke callback(ci,f,b, a) to generate  low part ouput
    '''
    for rx_enable in range(2**1):
        for sample_enable in range(2**1):
            for sample_bits in range(2**3):
                for counter in range(2**4):
                    for state in range(2**4):
                        callback(rx_enable,sample_enable, sample_bits, counter, state)


S_PRE = 0
S_SBIT = 1
S_D0 = 2
S_D1 = 3
S_D2 = 4
S_D3 = 5
S_D4 = 6
S_D5 = 7
S_D6 = 8
S_D7 = 9
S_DEND = 10


def gen(re, se, sbs, cnt, s):
    cnt_bin_str = bin(cnt)[2:].zfill(4)
    cnt = int(cnt_bin_str[::-1],2)
    #  |   FRAM0(START BIT)  |      FRAM1(D0)      |      FRAM2(D1)      |  ....|      FRAM8(D7)      |    FRAM9(STOP_BIT)  |
    #  | 0 1 2... 8 9...14 15| 0 1 2... 8 9...14 15| 0 1 2... 8 9...14 15|  ....| 0 1 2... 8 9...14 15| 0 1 2... 8 9...14 15|
    #  |_-_-_-..._-_-..._-_- |_-_-_-..._-_-..._-_- |_-_-_-..._-_-..._-_- |  ....|_-_-_-..._-_-..._-_- |_-_-_-..._-_-..._-_- |
    # --S_PRE|----S_SBIT-----|--------S_D0---------|--------S_D1---------|  ....|--------S_D7---------|-------S_STOP--------|
    #        ^      ^                     ^                     ^                            ^                            ^
    #        |      |                     |                     |                            |                            |
    #           sample here          sample here            sample here                 sample here                  back to S_PRE
    #                                                                                   RX_END here
    next_state = s
    cycle_count_en = 0
    shift_en = 0
    rx_bit = 0
    rec_end = 0

    if re:
        rx_count1 = bin(sbs).count('1')
        rx_bit = 1 if rx_count1 >= 2 else 0
        if S_SBIT <= s and s <= S_DEND:
            cycle_count_en = 1

        if not (S_PRE <= s and s <= S_DEND):
            next_state = S_PRE

        if s == S_D7 and cnt == 9:
            rec_end = 1

        if se:
            if s == S_PRE:
                if cnt == 2 and rx_bit == 0:
                    next_state = S_SBIT
                    cycle_count_en = 1

            elif S_SBIT <= s and s <= S_D7:
                if cnt == 15:
                    next_state = s + 1
                if cnt == 9:
                    shift_en = 1
            elif s == S_DEND:
                if cnt == 15:
                    next_state = S_PRE
    else:
        next_state = S_PRE

    return next_state | (cycle_count_en << 4) | (shift_en << 5) | (rx_bit << 6) | (rec_end << 7)


def gen_to_file(fname):
    d = bytearray()

    def write_one_byte(re, se, sbs, cnt, s):
        d.append(gen(re, se, sbs, cnt, s) & 0xFF)

    enum_input(write_one_byte)

    with open(fname, 'wb') as f:
        f.write(d)


usage = """
usage:
    receiver.py <ouput_file>
"""

if len(sys.argv) < 2:
    print(usage)
else:
    fname = sys.argv[1]
    gen_to_file(fname)
