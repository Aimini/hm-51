import core51
import core51_peripheral
import hex_decoder
import argparse
import random

parser = argparse.ArgumentParser(description="8051 simulator")
parser.add_argument('-i', '--input-file',   dest='input_file', action='store', help='input intel hex file')
parser.add_argument(
    '-d', '--dump-file', dest='dump_file', action='store', default=None,
    help="the text file to write ram and core register content. write hex number, 16 number each line, 8 lines total.")

dbgarg = ["-i",R"test\temp\75_MOV_d_i.hex"]

args = parser.parse_args()


run_flag = True
vm = core51.core51()
core51_peripheral.install_default_peripherals(vm)




    
def dump_core(core: core51.core51):
    if not args.dump_file:
        raise FileExistsError("No dump file configured.")

    ram_dump = list(core.IRAM)
    reg_dump = [core.SP, core.DPL, core.DPH, core.PSW, core.A, core.B]

    f = "0x{:0>2X}"
    with open(args.dump_file) as f:
        f.write(' '.join([f.format(_) for _ in reg_dump]))
        i = 0
        for x in ram_dump:
            if i % 16 == 0:
                f.write('\n')
            f.write(f.format(x))
            f.write(' ')


def normal_stop():
    global run_flag
    run_flag = False
    print("program exit.")


def assert_core(par0reg, par1reg, function_val):
    p0 = int(par0reg)
    p1 = int(par1reg)
    if function_val == 1:
        if not (p0 > p1):
            raise ArithmeticError("{} > {} assert failed".format(p0, p1))
    elif function_val == 2:
        if not (p0 == p1):
            raise ArithmeticError("{} == {} assert failed".format(p0, p1))
    if function_val == 3:
        if not (p0 < p1):
            raise ArithmeticError("{} < {} assert failed".format(p0, p1))

def assert_test(core):
    a = random.getrandbits(8)
    b = random.getrandbits(8)

    t = bytearray([
    # assert 0XFF == 0XFF
    0x75,0xFD,a,#            3     MOV 0xFD, #0x00])
    0x75,0xFE,b,#            4     MOV 0xFE, #0x00
    0x75,0xFF, #            5     MOV 0xFF,  ?
    ])
    condition = [
        [1, lambda a,b : a > b],
        [2, lambda a,b : a == b],
        [3, lambda a,b : a < b]
    ]

    for cmpcode in range(1,4):
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
            if cmpcode == x[0] and not (x[1](a,b)) and not take_exception: # assert failed but no exception
                raise e
            if cmpcode == x[0] and (x[1](a,b)) and  take_exception: # passed  but  exception happend
                raise e
            

def install_my_sfr(core: core51.core51):
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
    obj["DUMPR"].set_listener.append(lambda mem_obj, new_value: dump_core(core))
    obj["EXR"].set_listener.append(lambda mem_obj, new_value: normal_stop())
    obj["ASTREG"].set_listener.append(lambda mem_obj, new_value: assert_core(obj[p0], obj[p1], new_value))


install_my_sfr(vm)


# for _ in range(100):
#     assert_test(vm)


with open(args.input_file) as fh:
    data = hex_decoder.decode_ihex(fh.read())
    vm.load_rom(data)

vm.reset()
while run_flag:
    vPC = int(vm.PC)
    try:
        vm.step(1)
    except Exception as e:
        str(e)
        raise Exception(str(e) + " at PC[{:0>4X}]".format(vPC))
