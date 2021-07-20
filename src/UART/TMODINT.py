import sys
import argparse
##
## AI
## generate TMOD, INT combinational logic LUT\
# syncX are shift from MSB to LSB
pinconfig = [
    ("sync0" , 2),
    ("sync1" , 2),
    ("it0" , 1),
    ("it1" , 1),
    ("tr0" , 1),
    ("tr1" , 1),
    ("gate0" , 1),
    ("ct0" , 1),
    ("gate1" , 1),
    ("ct1" , 1),
]

def enum_input(pinconf, callback):
    '''
    '''

    totallen = 0
    for k,l in pinconf:
        totallen += l

    for x in range(1 << totallen):
        arg = {}
        t = x
        for k, l in pinconf:
            arg[k] = t & ((1<< l) - 1)
            t >>= l
        callback(arg) 

def gen_one(sync, it, tr, gate, ct):
    IE = 0
    CNTE = 0 
    _TR = 1 - tr
    XINTbit = (sync & 2) >> 1
    pXINTbit = sync & 1
    # rising edge, is represented by sync[0] == 0, sync[1] == 1
    int_pulse = 1 if(XINTbit == 1 and pXINTbit == 0) else 0
    
    #### generate IE,
    IE = int_pulse if it else XINTbit
    
    ### generate CNTE
    if ct == 0: # timmer
        if tr: # NEXTbit is opposite to the input logic level
            CNTE = (1 - XINTbit) if gate else 1
    else: # counter
        CNTE = int_pulse
            

    return IE, CNTE, _TR   

def gen(arg):
    sync0 = arg["sync0"]
    sync1 = arg["sync1"]
    it0 =   arg["it0"]
    it1 =   arg["it1"]
    tr0 =   arg["tr0"]
    tr1 =   arg["tr1"]
    gate0 = arg["gate0"]
    ct0 =   arg["ct0"]
    gate1 = arg["gate1"]
    ct1 =   arg["ct1"]

    IE0,CNTE0,_TR0 = gen_one(sync0, it0, tr0, gate0, ct0)
    IE1,CNTE1,_TR1 = gen_one(sync1, it1, tr1, gate1, ct1)

    return IE0 | (IE1 << 1) | (CNTE0 << 2)| (CNTE1 << 3)| (_TR0 << 4)| (_TR1 << 5)

    


def gen_to_file(fname):
    d = bytearray()

    def write_one_byte(arg):
        d.append(gen(arg) & 0xFF)

    enum_input(pinconfig, write_one_byte)

    with open(fname, 'wb') as f:
        f.write(d)


usage = """
usage:
    TMODINT.py <output_file>
"""

if len(sys.argv) < 2:
    print(usage)
else:
    fname = sys.argv[1]
    gen_to_file(fname)
