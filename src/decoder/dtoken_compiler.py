##################################################
# 2019-12-22 12:44:23
# AI
# dtoken compiler, compile all dtoken in all lines to
# machine code
# in physical level, we can treat a part of circuit
# to a component that have multiple input control.
# for example:
# RF(Register File) have three function input:
#   source select, write low and write high
# so we can using mark "LWE" to meaing write low,
# A meaing select reigiter 0 in RF.
#
# for most of paramter control mark, it's only using
# name parameter, we can just using a LUT to find encoding
# parameter encoding.
# for another control mark, we using special logic to encode it.
##################################################
import enum
import dtoken
###########################################################
# parmater name encoding LUT
# for one component(RF, WR, SR or other component), we have
# LUT organized like below:
#  [
#    [ [how many bits to encode it], [name0, name1 ,name2, ...] # each name's value corresponding to it's index
#   [  [same meaing as above],       [name0, name1 ,name2, ...]
#    ...
# ]
#  the placement of the control encoding is calculated automatically.
#   after calculate:
#  [
#    [[start position in control signals bits, how many bits to encode it], [name0, name1 ,name2, ...] # each name's value corresponding to it's index
#   [ [same meaing as above,                   same meaing as above],      [name0, name1 ,name2, ...]
#    ...
# ]
# if we found '-' in the postion's place,
#    [['-', how many bits to encode it], [name0, name1 ,name2, ...]]
#  it's meaning this parameter share the n(length) of the bits of the previous parameters  for encoding.
# we must
###########################################################

# register file control label encoding

REGISTER_FILE = [
    #,[len, (position)], [name_seq(0,2,3,...)]
    [[4], [
        "A",   "B",  "SP", "PSW",
        "DPL", "DPH", "IE", "IP",
        "PCL", "PCH", "IR", "T0",
        "T1",  "T2",  "T3"]],
    [[1], ["", "LWE"]],
    [[1], ["", "HWE"]],
    [[2, '-'], ["", "", "", "WE"]]
]

BUS = [
    [[3], ["Z", "ALUS", "ALUD", "IMMED", "RAM", "XRAM", 'ROM', 'IRQ']]
]

WR = [
    [[1], ["", "WE"]]
]

SR = [
    [[1], ["", "WE"]]
]


BR = [
    [[3], ["", "WE"]]
]
ALUD = [
    [
        [4], [
            ["ORL", "PF"], ["ANL", "ZF"], "XRL", "B",
            "ADD",  "ADDC", "SUBB", "DA",
            "SHIRQN", "IRQN2IRQ", "EXTB", "INSB",
            "ADDR11REPLACE", "SETPSWF", "Ri", "Rn"]
    ]
]

ALUS = [
    [
        [4, '-'], ["A", "NOTA", "CAA", "SETPF"
                   "RR", "RL", "RRC", "RLC",
                   "INC", "DEC", "BADDR", "BIDX",
                   "SSETCY", "SETOVCLRCY", "CHIRQ", "SWAP"]
    ]
]


##################
# parmater name encoding LUT LUT to make a big compoent LUT
COM_LUT = {
    "RF": REGISTER_FILE,
    "BUS": BUS,
    "WR": WR,
    "SR": SR,
    "BR": BR,
    "ALUD": ALUD,
    "ALUS": ALUS,
}


### jump encode
### jump using position to encode parameter value
JUMP_LUT = [
    [[3], ["JMP", "JLT", "JGT", "JEQ", "", "JBIT", ""]],  # jump type encode
    # control parameters len
    #immed, address
    [[8],   [13]]
]
    ## alu function encode
    ## alud alu alus uisng common input as function control



class dtoken_compiler:

    def __init__(self, address_space, COM_LUT=COM_LUT, JUMP_LUT=JUMP_LUT):
        """
        parameter:
            address_space: int
                provide rom capacity info, 2**address_space bytes
        """
        self.capacity= 2**address_space
        self.COM_LUT= COM_LUT
        self.JUMP_LUT= JUMP_LUT
        self.calcuate_encoding_position()

    def reset(self):
        self.pc= 0
        self.jump_table= {}  # store jump label address, jump_label:string -> pc_address: int
        self.pure_dtokens= []  # dtokens without jump dtokens, [[lineno,dtoken_list],[lineno,dtoken_list]...]
        self.rom= []        # store machine code

    def extend_rom(self):
        while len(self.rom) <= self.pc:
            self.rom.append(None)

    def pc_inc(self):
        self.pc += 1

    def set_pc(self, pc):
        self.pc= pc
        self.extend_rom()

    def calcuate_encoding_position(self):
        """

        """
        pos= 0

        def check_one_lut(l, pos):
            if len(l) == 2:  # only len info in parameter_LUT
                if l[1] == '-':
                    l[1] = pos - l[0]
                    return pos
            l.append(pos)
            return pos + l[0]

        for k, v in self.COM_LUT.items():  # v = RF LUT , WR LUT ...
            for one in v:  # one = RF's [A,B,PSW] parameter LUT or RF's LWE parameter LUT, HWE or WR's ...
                pos = check_one_lut(one[0], pos)

        pos= check_one_lut(self.JUMP_LUT[0][0], pos)
        for p in self.JUMP_LUT[1]:  # position parameter
            pos= check_one_lut(p, pos)

    def find_parameter_encoding_info(self, p, LUT):
        """
        find parameter
        """
        place_info= None  # parameter encoding info [start, len]
        index= None
        for x in LUT:
            try:
                # find parameter name in one parameter LUST

                index= x[1].index(p)
                place_info= x[0]
                break
            except ValueError as e:
                pass  # not found , next lut
        return place_info, index

    def convert_one_token(self, dt):
        if dt.type == dtoken.PAR_CONTROL:
            parameter_LUTs= self.COM_LUT.get(dt.value)
            if parameter_LUTs is None:
                raise SyntaxError('unkonw control name "{}" at line {{}}'.format(dt.value))

            print('encoding control"{}":'.format(dt.value))
            for p in dt.parameters:
                place_info, index= self.find_parameter_encoding_info(p, parameter_LUTs)

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

    def gen_pure_token(self, dtoken_lines):
        for lineno, one in dtoken_lines:
            a= []
            for x in one:
                v= x.value
                if x.type != dtoken.JUMP_MARK:
                    a.append(x)
                else:
                    if self.jump_table.get(v) is not None:
                        raise SyntaxError('duplicate jump label "{}" at line'.format(v))
                    self.jump_table[v]= self.pc

            if len(a) > 0:
                self.pc_inc()
                self.pure_dtokens.append([lineno, a])

    def compile(self, dtoken_lines):
        self.reset()
        self.gen_pure_token(dtoken_lines)
        self.pc= 0

        for lineno, one in self.pure_dtokens:
            try:
                self.convert_one_line(one)
                self.pc_inc()
            except SyntaxError as e:
                e.msg= e.msg.format(lineno)
                print(e)
