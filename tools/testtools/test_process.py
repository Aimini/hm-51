import subprocess
import sys
import pathlib
from compile import compile
import argparse


class test_process():
    F_NEW_ASM = "FGEN_NEW_ASM"
    F_NEW_HEX = "FGEN_NEW_HEX"
    F_SIM_INSTRUCTION = "FSIM_INSTRUCTION"
    F_DUMP_DATA_BUS = "F_DUMP_DATA_BUS"
    F_SIM_CIRCUIT = "FSIM_CIRCUIT"
    F_VERIFY = "F_VERIFY"

    def __init__(self, gen_filename_str, temp_dir_str):
        self.filename = pathlib.Path(gen_filename_str)
        self.tempdir = pathlib.Path(temp_dir_str)
        filestem = self.filename.stem
        self.asmfile = self.tempdir / (filestem + ".A51")
        self.hexfile = self.tempdir / (filestem + ".hex")

        self.flags = []
        self.run_config = [
            [test_process.F_NEW_ASM, 'generate assembly', self.genasm],
            [test_process.F_NEW_HEX, 'compile', self.compile],
            [test_process.F_SIM_INSTRUCTION, 'instruction simulate', self.simulate_instruction],
            [test_process.F_SIM_CIRCUIT, 'circuit simulate', self.simulate_hardware],
            [test_process.F_VERIFY, 'verify', self.verify],
        ]
        
        self.output = bytearray()

    def addflag(self, flag):
        self.flags.append(flag)
        return self

    def _run_subprocess(self, cmd):
        s = subprocess.run(cmd, capture_output=True)
        self.output.extend(s.stdout)
        self.output.extend(b'\n')
        self.output.extend(s.stderr)
        return s.returncode

    def run(self):
        for flag, name, call in self.run_config:
            if flag not in self.flags:
                continue

            print(f">>>>>>>>>>>>> {name}")
            rt = call()

            if rt != 0:
                print(f"error occur at {name} stage.")
                return rt
        return 0
            
            

    def genasm(self):
        filename = self.filename

        returncode = self._run_subprocess(['python', filename, '-o', self.tempdir])
        return returncode

    def compile(self):
        filename = self.asmfile
        hexfile = self.hexfile

        returncode = compile(filename, hexfile)
        return returncode

    def simulate_instruction(self):
        rom_file = self.hexfile
        simulator_exe = pathlib.Path(R"tools\51sim.py")

        self.simulate_instruction_dump_file_template = self.tempdir / \
            (rom_file.stem + ".simulate_instruction.dump-%d.txt")
        returncode = self._run_subprocess(['python', simulator_exe,
                                     '-i', rom_file,
                                     '-d', self.simulate_instruction_dump_file_template])
        return returncode

    def simulate_hardware(self):
        rom_file = self.hexfile
        self.simulate_hardware_dump_file_template = self.tempdir / (rom_file.stem + ".simulate_hardware.dump-%d.txt")
        self.dump_data_bus_file = self.tempdir / (rom_file.stem + ".data_bus.bin")
        simulator_exe = pathlib.Path(R"tools\Digitalc.jar")
        cirucit_file = pathlib.Path(R"src\circuit\TOP.dig")
        ds_file = pathlib.Path(R"eeprom-bin\decoder.bin")

        cmd = ['java', '-jar', simulator_exe,
                                     '-c',cirucit_file, 
                                     '-d',ds_file,
                                     '-r', rom_file,
                                     '-F',self.simulate_hardware_dump_file_template]
        if self.F_DUMP_DATA_BUS in self.flags:
            cmd.extend(('-B', self.dump_data_bus_file))
        returncode = self._run_subprocess(cmd)
        return returncode

    def verify(self):
        count = 0
        while True:
            fsname = str(self.simulate_instruction_dump_file_template) % count
            fhname = str(self.simulate_hardware_dump_file_template) % count
            if not pathlib.Path(fsname).exists() and not pathlib.Path(fhname).exists():
                return 0

            fs = open(fsname)
            fh = open(fhname)
            sresult = [int(_, 0) for _ in fs.read().split()]
            hresult = [int(_, 0) for _ in fh.read().split()]

            if sresult != hresult:
                print("verify failed:")
                print(f"\t{fsname}")
                print(f"\t{fhname}")
                return -1

            count += 1
        return 0


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-A', '--genearte-assemble-file',
                            dest='genearte_assemble', action='store_const', const=True, default=False,
                            help='generate new assemble file from script')
    arg_parser.add_argument('-H', '--generate-hex-file',
                            dest='generate_hex', action='store_const', const=True, default=False,
                            help='generate new hex file from assemble file, the assemble file should in output directory')
    arg_parser.add_argument('-I', '--instruction-simulation',
                            dest='instruction_simulation', action='store_const', const=True, default=False,
                            help='simulate instructions with hex file, the hex file should in output directory')
    arg_parser.add_argument('-C', '--circuit-simulation',
                            dest='circuit_simulation', action='store_const', const=True, default=False,
                            help='simulate circuit with hex file, the hex file should in output directory')
    arg_parser.add_argument(
        '-V', '--verify', dest='verify', action='store_const', const=True, default=False,
        help='verify the output of the instructions simulation and circuit simulation, the dump'
        'file of the simulation should in output directory')
    arg_parser.add_argument(
        '-B', '--data-bus', dest='data_bus', action='store_const', const=True, default=False,
        help='dump data_bus'
        'file of the simulation should in output directory')

    arg_parser.add_argument('-f', '--script-file', action='store', type=str, dest='script_file')
    arg_parser.add_argument('-o', '--output-dir', action='store', type=str, dest='output_dir')

    args = arg_parser.parse_args()

    t = test_process(args.script_file, args.output_dir)
    if args.genearte_assemble:
        t.addflag(test_process.F_NEW_ASM)
    if args.generate_hex:
        t.addflag(test_process.F_NEW_HEX)
    if args.instruction_simulation:
        t.addflag(test_process.F_SIM_INSTRUCTION)
    if args.circuit_simulation:
        t.addflag(test_process.F_SIM_CIRCUIT)
    if args.verify:
        t.addflag(test_process.F_VERIFY)
    if args.data_bus:
        t.addflag(test_process.F_DUMP_DATA_BUS)
    ec = t.run()
    print(t.output.decode('utf8'))
    print("program exit with code {}.".format(ec))
    exit(ec)
