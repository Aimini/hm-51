import subprocess
import sys
import pathlib
from compile import compile
import databus2py
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

        self.simulate_instruction_dump_file = self.tempdir / \
            (rom_file.stem + ".simulate_instruction.dump.txt")
        returncode = self._run_subprocess(['python', simulator_exe,
                                     '-i', rom_file,
                                     '-d', self.simulate_instruction_dump_file])
        return returncode

    def simulate_hardware(self):
        rom_file = self.hexfile
        self.simulate_hardware_dump_file = self.tempdir / (rom_file.stem + ".simulate_hardware.dump.txt")
        self.dump_data_bus_file = self.tempdir / (rom_file.stem + ".data_bus.bin")
        self.dump_data_bus_py_file = self.tempdir / (rom_file.stem + ".data_bus.py")
        simulator_exe = pathlib.Path(R"tools\Digitalc.jar")
        cirucit_file = pathlib.Path(R"src\circuit\TOP.dig")
        ds_file = pathlib.Path(R"eeprom-bin\decoder.bin")

        cmd = ['java', '-jar', simulator_exe,
                                     '-c',cirucit_file, 
                                     '-d',ds_file,
                                     '-r', rom_file,
                                     '-F',self.simulate_hardware_dump_file]
        if self.F_DUMP_DATA_BUS in self.flags:
            cmd.extend(('-B', self.dump_data_bus_file))

        returncode = self._run_subprocess(cmd)
        if returncode == 0 and self.F_DUMP_DATA_BUS in self.flags:
            databus2py.convert(self.dump_data_bus_file, self.dump_data_bus_py_file)
        return returncode

    def verify(self):
        fsname = self.simulate_instruction_dump_file
        fhname = self.simulate_hardware_dump_file
        if not pathlib.Path(fsname).exists() and not pathlib.Path(fhname).exists():
            return 0

        fs = open(fsname).read()
        fh = open(fhname).read()
        all_sresult = [_ for _ in fs.split(';') if len(_)]
        all_hresult = [_ for _ in fh.split(';') if len(_)]



        for i, simulation_dump in enumerate(all_sresult):
            sresult = [int(_, 0) for _ in simulation_dump.split()]
            hresult = [int(_, 0) for _ in   all_hresult[i].split()]
            
            


            if sresult != hresult:
                def search_nth_dump(fname,fcontents:str):
                    nth_semicolon = 0
                    previous_split_lineno = 1
                    for linesub1, line_str in enumerate(fcontents.splitlines()):
                        if line_str.find(';') != -1:
                            if nth_semicolon == i:
                                print(f'  from File "{str(fname)}", line {previous_split_lineno}.')
                                return
                            previous_split_lineno = linesub1 + 1 
                            nth_semicolon += 1
                
                print(f"verify failed at {i + 1}th dump:")
                search_nth_dump(fsname, fs)
                search_nth_dump(fhname, fh)
                return -1

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

    arg_parser.add_argument('-f', '--script-file', action='store', type=str, dest='script_file', required=True)
    arg_parser.add_argument('-o', '--output-dir', action='store', type=str, dest='output_dir', required=True)

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
