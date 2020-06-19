import subprocess
import sys
import pathlib
import os
import random
import string


class test_process():
    def __init__(self, asm_filename_str, temp_dir_str):
        self.filename =  pathlib.Path(asm_filename_str)
        self.tempdir = pathlib.Path(temp_dir_str)

    def run(self):
        print("\n\n>>>>>>>>>>>>> compile")
        rt = self.compile()
        if rt != 0:
            print("\n\nerror occur at compile stage.")
            return rt
            
        print("\n\n>>>>>>>>>>>>> instruction simulate")
        rt = self.simulate_instruction()
        if rt != 0:
            print("\n\nerror occur at instruction simulate stage.")
            return rt
        
        print("\n\n>>>>>>>>>>>>> hardware simulate")
        rt = self.simulate_hardware()
        if rt != 0:
            print("\n\nerror occur at hardware simulate stage.")
            return rt

        print("\n\n>>>>>>>>>>>>> verify")
        rt = self.verify()
        if rt != 0:
            print("\n\nerror occur at verify stage.")
            return rt
        return 0

    def compile(self):
        filename = self.filename
        filestem = filename.stem

        hexfile =  self.tempdir  / (filestem + ".hex")

        returncode = subprocess.run(f"python test\\compile.py {filename} {hexfile}").returncode

        self.rom_file = hexfile
        return returncode


    def simulate_instruction(self):
        rom_file = self.rom_file
        simulator_exe = pathlib.Path(R"tools\py51\51sim.py")
        
        self.simulate_instruction_dump_file_template = self.tempdir  / (rom_file.stem + ".simulate_instruction.dump-%d.txt")
        returncode = subprocess.run(['python',simulator_exe,
            '-i', rom_file,
            '-d', self.simulate_instruction_dump_file_template]).returncode
        return returncode


    def simulate_hardware(self):
        rom_file = self.rom_file
        self.simulate_hardware_dump_file_template = self.tempdir  / (rom_file.stem + ".simulate_hardware.dump-%d.txt")
        simulator_exe = pathlib.Path(R"tools\Digitalc.jar")
        cirucit_file =  pathlib.Path(R"src\circuit\TOP.dig")
        ds_file =  pathlib.Path(R"eeprom-bin\decoder.bin")
        returncode = subprocess.run(['java','-jar',simulator_exe,
            cirucit_file,ds_file, rom_file,
             self.simulate_hardware_dump_file_template]).returncode
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
            sresult = [int(_,0) for _ in fs.read().split()]
            hresult = [int(_,0) for _ in fh.read().split()]
            
            if sresult != hresult:
                print("verify failed:")
                print(f"\t{fsname}")
                print(f"\t{fhname}")
                return -1

            count += 1
        return 0

usage = """
usage:
    compile_all <input_file> <temporary_dir>
    input_file:
        51 assembly file
    temporary_dir:
        directory to store all temporary file and target intel hex format file.
"""

if len(sys.argv) < 3:
    print(usage)
else:
    t = test_process(sys.argv[1], sys.argv[2])
    ec = t.run()
    print("program exit with code {}.".format(ec))
    exit(ec)