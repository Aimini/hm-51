import core51
import core51_peripheral
import hex_decoder
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
dump_count = 0


vm = core51.core51()
core51_peripheral.install_default_peripherals(vm)


def dump_core(core: core51.core51, fh):
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

    def dump_core_to_template_file():
        global dump_count
        with open(args.dump_file_template % dump_count, "w") as fh:
            dump_core(core, fh)
            dump_count += 1

    obj["DUMPR"].set_listener.append(lambda mem_obj, new_value: dump_core_to_template_file())
    obj["EXR"].set_listener.append(lambda mem_obj, new_value: normal_stop())
    obj["ASTREG"].set_listener.append(lambda mem_obj, new_value: assert_core(obj[p0], obj[p1], new_value))


install_my_sfr(vm)


# for _ in range(3):
#     assert_and_dump_test(vm)


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
