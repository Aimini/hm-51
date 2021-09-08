from random import expovariate
import sys
import importlib.util
from typing import Tuple

py51path = '../Code/py51'
sys.path.append(py51path)
py51notfund = False
try:
    if importlib.util.find_spec("py51") is None:
        py51notfund = True
except ModuleNotFoundError:
    py51notfund = True

if py51notfund:
    raise Exception("py51 not found in folder {!r}, please check the <py51path> in file {!r} or using customized simulator.".format(py51path,sys.argv[0]))

from py51 import create_stand51,core51,hex_decoder
import argparse
import random
import sys

parser = argparse.ArgumentParser(description="8051 simulator")
parser.add_argument('-i', '--input-file',   dest='input_file', action='store', help='input intel hex file')
parser.add_argument(
    '-d', '--dump-file-template', dest='dump_file_template', action='store', default=None,
    help='The text file name to write ram and core register content, using C style format. '
    'for example you can write "dump-%%d.txt", and the first dump will write to file "dump-0.txt, "'
    'the second dump will write to file "dump-1.txt".  Sequence is - SP DPL DPH IE IP PSW A B, IRAM 0x00 - 0x7F.')

dbgarg = ["-i", R"test\temp\75_MOV_d_i.hex"]

args = parser.parse_args()


run_flag = True


vm = create_stand51()


def dump_core(core: core51, fh):
    ram_dump = list(core.IRAM)
    reg_dump = [core.SP, core.DPL, core.DPH, core.PSW, core.A, core.B]

    fh.write(' '.join(['{}'.format(_) for _ in reg_dump]))
    fh.write('\n')
    i = 0
    for x in ram_dump:
        fh.write('{}'.format(x))
        fh.write(' ')
        i += 1
        if i % 16 == 0:
            fh.write('\n')
    fh.write(';')


def normal_stop():
    global run_flag
    run_flag = False
    print("program exit.")


def assert_core(par0reg, par1reg, function_val):
    p0 = int(par0reg)
    p1 = int(par1reg)
    if function_val == 1:
        if not (p0 > p1):
            raise ArithmeticError("{} > {} assert failed".format(hex(p0), hex(p1)))
    elif function_val == 2:
        if not (p0 == p1):
            raise ArithmeticError("{} == {} assert failed".format(hex(p0), hex(p1)))
    if function_val == 3:
        if not (p0 < p1):
            raise ArithmeticError("{} < {} assert failed".format(hex(p0), hex(p1)))
    if function_val == 4:
            raise Exception("user actively requested a crash.")

ADDR_SIZE = 0x1D
ADDR_PCL = 0x1E
ADDR_PCH = 0x1F
ADDR_CHUCK = 0x20
ROM_LOCK = True
SEQ_DISALBE_SDP =(
    (0xAA, 0x5555),(0x55, 0x2AAA),(0x80, 0x5555),
    (0xAA, 0x5555),(0x55, 0x2AAA),(0x20, 0x5555))
SEQ_ENALBE_SDP = (
    (0xAA, 0x5555),(0x55, 0x2AAA),(0xA0, 0x5555))
def uf_programROM(core):
    if int(core.PSW) & 2 == 0:
        return
    if int(core.A) ^ int(core.B) != 0xFF:
        return
        
    # print(hex(vPC))
    global ROM_LOCK
    valA = int(core.A)
    if valA == 0:
        if ROM_LOCK:
            return
        size = int(core.IRAM[ADDR_SIZE])
        PC = (int(core.IRAM[ADDR_PCH])<< 8) + int(core.IRAM[ADDR_PCL])
        for i in range(len(core.ROM), PC + size):
            core.ROM.append(0)
        for i in range(size):
            core.ROM[PC + i] = int(core.IRAM[ADDR_CHUCK + i])
    elif valA == 1:
        size = int(core.IRAM[ADDR_SIZE])
        writing_seq = []
        for i in range(size):
            offset = i*3 + ADDR_SIZE + 1
            data = int(core.IRAM[offset])
            PC = (int(core.IRAM[offset + 2])<< 8) + int(core.IRAM[offset + 1])
            writing_seq.append((data, PC))
        
        writing_seq = tuple(writing_seq)

        if writing_seq == SEQ_DISALBE_SDP:
            ROM_LOCK = False
        elif writing_seq == SEQ_ENALBE_SDP:
            ROM_LOCK = True
 
        
def assert_and_dump_test(core):
    a = random.getrandbits(8)
    b = random.getrandbits(8)

    t = bytearray([
        # assert 0XFF == 0XFF
        0x75, 0xFD, a,  # 3     MOV 0xFD, #0x00])
        0x75, 0xFE, b,  # 4     MOV 0xFE, #0x00
        0x75, 0xFF,  # 5     MOV 0xFF,  ?
    ])
    condition = [
        [1, lambda a, b: a > b],
        [2, lambda a, b: a == b],
        [3, lambda a, b: a < b],
        [4, lambda a, b: False]
    ]

    for cmpcode in range(1, 4):
        c = bytearray(t)
        take_exception = False
        c.append(cmpcode)
        core.reset()
        core.load_rom(c)
        try:
            core.step(3)
        except ArithmeticError as e:
            take_exception = True

        for x in condition:
            e = Exception("assert function error.")
            if cmpcode == x[0] and not (x[1](a, b)) and not take_exception:  # assert failed but no exception
                raise e
            if cmpcode == x[0] and (x[1](a, b)) and take_exception:  # passed  but  exception happend
                raise e
    dump_core(core, sys.stdout)

dump_fh = None
def install_my_sfr(core: core51):
    p0 = "ASTPAR0"
    p1 = "ASTPAR1"
    my_sfr = {
        0xFB: "DUMPR",
        0xFC: "EXR",
        0xFD: p0,
        0xFE: p1,
        0xFF: "ASTREG",
    }

    obj = core.sfr_extend(my_sfr)
    
   
    def dump_core_to_template_file():
        global dump_fh
        if dump_fh is None:
            dump_fh = open(args.dump_file_template, "w")
        dump_core(core, dump_fh)

    obj["DUMPR"].set_listener.append(lambda mem_obj, new_value: dump_core_to_template_file())
    obj["EXR"].set_listener.append(lambda mem_obj, new_value: normal_stop())
    obj["ASTREG"].set_listener.append(lambda mem_obj, new_value: assert_core(obj[p0], obj[p1], new_value))


install_my_sfr(vm)
vm.reserved_instruction = uf_programROM

# for _ in range(3):
#     assert_and_dump_test(vm)


with open(args.input_file) as rom_fh:
    data = hex_decoder.decode_ihex(rom_fh.read())
    vm.load_rom(data)

vm.reset()
while run_flag:
    vPC = int(vm.PC)
    # try:
    vm.step(1)
    # except Exception as e:
    #     str(e)
    #     raise Exception(str(e) + " at PC[{:0>4X}]".format(vPC))
