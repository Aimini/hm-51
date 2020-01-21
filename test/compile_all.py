import subprocess
import sys
import pathlib
import os
class trysubp():
    """
    provide subprocess chain, if one subprocess in chain return code is not 0,
    then subprocess will stop excute consecutive subprocesses.
    usage:
        ret = trysubp.build(arg_to_subprocess0)
            .chain(arg_to_subprocess1)
            .chain(arg_to_subprocess1)
            .chain(arg_to_subprocess1)
            .chain(arg_to_subprocess1)
            ...
        ret is the failed subprocess(if have, you can check ret's return code)
    """
    def __init__(self,*args, **kargs):
        """
        args, kargs:
            arguments pass to subprocess
        """
        self.returncode = subprocess.run(*args, **kargs).returncode


    def chain(self, *args, **kargs):
        if self.returncode == 0:
            return trysubp(*args, **kargs)
        else:
            return self
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

        objfile =  self.tempdir  / (filestem + ".obj")
        absfile =  self.tempdir  / (filestem + ".abs")
        hexfile =  self.tempdir  / (filestem + ".hex")
        tooldir = pathlib.Path(R"C:\Keil_v5\C51\BIN")
        A51 = tooldir / 'A51.exe'
        BL51 = tooldir / 'BL51.exe'
        OH51 = tooldir / 'OH51.exe'

        rp = trysubp(f"{A51} {filename} OBJECT({objfile})")\
            .chain(f"{BL51} {objfile} TO {absfile}")\
            .chain(f"{OH51} {absfile}  HEXfile({hexfile})")

        self.rom_file = hexfile
        return rp.returncode


    def simulate_instruction(self):
        rom_file = self.rom_file
        simulator_exe = pathlib.Path(R"tools\py51\51sim.py")
        
        self.simulate_instruction_dump_file_template = self.tempdir  / (rom_file.stem + ".simulate_instruction.dump-%d.txt")
        rp = trysubp(['python',simulator_exe, '-i', rom_file, '-d', self.simulate_instruction_dump_file_template])
        return rp.returncode


    def simulate_hardware(self):
        rom_file = self.rom_file
        self.simulate_hardware_dump_file_template = self.tempdir  / (rom_file.stem + ".simulate_hardware.dump-%d.txt")
        simulator_exe = pathlib.Path(R"tools\Digitalc.jar")
        cirucit_file =  pathlib.Path(R"src\circuit\CORE.dig")
        ds_file =  pathlib.Path(R"eeprom-bin\decoder.bin")
        rp = trysubp(['java','-jar',simulator_exe, cirucit_file,ds_file, rom_file, self.simulate_hardware_dump_file_template])
        return rp.returncode

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
    compile_all <input_file> <template_dir>
    input_file:
        51 assembly file
    template_dir:
        directory to store output file,it's an intel hex format file, and it have the same name as input file.
"""

if len(sys.argv) < 3:
    print(usage)
else:
    t = test_process(sys.argv[1], sys.argv[2])
    ec = t.run()
    print("program exit with code {}.".format(ec))
    exit(ec)