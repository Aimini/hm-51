import core51
import core51_peripheral
import hex_decoder
import argparse

parser = argparse.ArgumentParser(description="8051 simulator")
parser.add_argument('-i', '--input-file',   dest='input_file', action='store', help='input intel hex file')
parser.add_argument('-r', '--ram-dump-file',     dest='ram_dump', action='store', default=None,
                    help="the text file to write ram content. write hex number, 16 number each line, 8 lines total.")
parser.add_argument('-c', '--core-reg-dump-file', dest='core_reg_dump', action='extend', default=None,
                    help="the text file to save core register, A, B, SP, PSW, DPTR.")

args = parser.parse_args()


vm = core51.core51()
core51_peripheral.install_default_peripherals(vm)


with open(args.input_file) as fh:
    data = hex_decoder.decode_ihex(fh.read())
    vm.load_rom(data)
SCON = vm.get_sfr("SCON")
SBUF = vm.get_sfr("SBUF")


def print_sbuf(mem_obj, new_val):
    print(chr(new_val), end='', flush=True)
    SCON[1] = 1


SBUF.set_listener.append(print_sbuf)
vm.reset()
vm.run()
