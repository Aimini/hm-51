##########################################
# 2019-12-22 12:44:23
# AI
# dtoken compiler, compile all dtoken in all lines to
# machine code
##########################################
import enum
import dtoken
##########
# register file control label encoding
REGISTER_FILE = [
    #[start,len],[name_seq(0,2,3,...)]
    [[3, 4], [
        "A",   "B",  "SP", "PSW",
        "DPL", "DPH", "IE", "IP",
        "PCL", "PCH", "IR","T0",
        "T1",  "T2",  "T3"]],
    [[7, 1], ["", "LWE"]],
    [[7, 1], ["", "HWE"]],
    [[7, 2], ["", "", "", "WE"]]
]

BUS = [
    [[9, 3], "Z", "ALUS", "ALUD", "IMMED", "RAM", "XRAM", 'ROM', 'IRQ']
]

WR = [
    [[12, 1], ["", "WE"]]
]

SR = [
    [[13, 1], ["", "WE"]]
]


BR = [
    [[14, 3], ["", "WE"]]
]

#ALU FUNCTION
ALUD = [
    [
        [17, 4],
        [
            ["ORL", "PF"], ["ANL", "ZF"], "XRL", "B",
            "ADD",  "ADDC", "SUBB", "DA",
            "SHIRQN", "IRQN2IRQ", "EXTB", "INSB",
            "ADDR11REPLACE", "SETPSWF", "Ri", "Rn"
        ]
    ]
]

ALUS = [
    [
        [17, 4], 
        ["A", "NOTA", "CAA", "SETPF"
        "RR", "RL", "RRC", "RLC",
        "INC", "DEC", "BADDR", "BIDX",
        "SSETCY", "SETOVCLRCY", "CHIRQ", "SWAP"]
    ]
]

# a
GEN_LUT = {
    "RF": REGISTER_FILE,
    "BUS": BUS,
    "WR": WR,
    "SR": SR,
    "BR": BR,
    "ALUD": ALUD,
    "ALUS": ALUS
}


class dtoken_compiler:

    def __init__(self, address_space, LUT = GEN_LUT):
        """
        parameter:
            address_space: int
                provide rom capacity info, 2**address_space bytes
        """
        self.capacity = 2**address_space
        self.LUT = LUT

    def reset(self):
        self.pc = 0
        self.jump_table =   {} # store jump label address, jump_label:string -> pc_address: int
        self.pure_dtokens = [] # dtokens without jump dtokens, [[lineno,dtoken_list],[lineno,dtoken_list]...]
        self.rom = []        # store machine code

    def extend_rom(self):
        while len(self.rom) <= self.pc:
            self.rom.append(None)

    def pc_inc(self):
        self.pc += 1

    def set_pc(self, pc):
        self.pc = pc
        self.extend_rom()

    def convert_one_token(self, dt):
        if dt.type == dtoken.PAR_CONTROL:
            parameter_LUTs = self.LUT.get(dt.value)
            if parameter_LUTs is None:
                raise SyntaxError('unkonw control name "{}" at line {{}}'.format(dt.value))

            print('encoding control"{}":'.format(dt.value))
            for p in dt.parameters:
                place_info = None # parameter encoding info [start, len]
                index = None      # 
                for x in parameter_LUTs:
                    try:
                        # find parameter name in one parameter LUST
                        index = x[1].index(p)
                        place_info = x[0]
                        break
                    except ValueError as e:
                        pass # not found , next lut

                if place_info is None:
                    raise SyntaxError('unkonw control parameter "{}" at line {{}}'.format(p))

                print('parameter "{}"({}) at {}:'.format(p, index, place_info))
        pass

    def convert_one_line(self, dtokens):
        """
        convert one lines token to machine code
        """
        for one in dtokens:
                self.convert_one_token(one)
    

    def gen_pure_token(self,dtoken_lines):
        for lineno, one in dtoken_lines:
            a = []
            for x in one:
                v = x.value
                if x.type != dtoken.JUMP_MARK:
                    a.append(x)
                else:
                    if self.jump_table.get(v) is not None:
                        raise SyntaxError('duplicate jump label "{}" at line'.format(v))
                    self.jump_table[v] = self.pc

            if len(a) > 0:
                self.pc_inc()
                self.pure_dtokens.append([lineno,a])

    def compile(self, dtoken_lines):
        self.reset()
        self.gen_pure_token(dtoken_lines)
        self.pc = 0

        for lineno, one in self.pure_dtokens:
            try:
                self.convert_one_line(one)
                self.pc_inc()
            except SyntaxError as e:
                e.msg = e.msg.format(lineno)
                print(e)
