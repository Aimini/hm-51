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
import control_LUT


class dtoken_compiler:
    def __init__(self, CTL_LUT=control_LUT.CTL_LUT):
        """
        parameter:
            address_space: int
                provide rom capacity info, 2**address_space bytes
        """
        self.CTL_LUT = CTL_LUT
        self.calcuate_LUT_parameters_position()

    def reset(self):
        self.pc = 0
        self.jump_table = {}  # store jump label address, jump_label:string -> pc_address: int
        self.hl_dtokens = []  # hardware level dtokens, [[lineno,dtoken_list],[lineno,dtoken_list]...]
        self.rom = []        # store machine code

    def extend_rom(self):
        while len(self.rom) <= self.pc:
            self.rom.append(None)

    def pc_inc(self):
        self.pc += 1
        self.extend_rom()

    def set_pc(self, pc):
        self.pc = pc
        self.extend_rom()

    def calcuate_LUT_parameters_position(self):
        pos = 0
        for k, v in self.CTL_LUT.items():  # v = RF LUT , WR LUT ...
            pos = v.auto_position(pos)

    def controls_parameters_position_info(self):
        pi = []
        for k, v in self.CTL_LUT.items():
            pi.extend([(x[0], x[1], k + '_' + x[2]) for x in v.position_info()])
        return pi

    def find_parameter_encoding_info(self, i, p, LUT):
        """
        find parameter's place info and encoding
        return:
            place_info:tuple, encoding:int
                place_info:(pos:int, len:int)
        """
        if isinstance(LUT, control_LUT.name_parameters_lut):
            return LUT.get_info(p)
        elif isinstance(LUT, control_LUT.value_parameter_lut):
            return LUT.get_place_info(i), p

    def convert_one_token(self, dt):
        control_parameter_LUTs = self.CTL_LUT.get(dt.value)
        if control_parameter_LUTs is None:
            raise SyntaxError('unkonw control name "{}"'.format(dt.value))

        for i, p in enumerate(dt.parameters):
            place_info, encoding = self.find_parameter_encoding_info(i, p, control_parameter_LUTs)

            if place_info is None:
                raise SyntaxError('unkonw control parameter "{}"'.format(p))

            # jump mark in address, etc.
            if not isinstance(encoding, int):
                encoding = self.jump_table.get(encoding)

            if not isinstance(encoding, int):
                print(dt)
                raise SyntaxError('unkonw control parameter "{}"'.format(p))

    def convert_one_line(self, dtokens):
        """
        convert one lines token to machine code
        """
        for one in dtokens:
                self.convert_one_token(one)

    def split_jump_dtoken(self, dtoken_lines):
        """
            generate hardware level dtoken that will convert to machine code
            1. remove jump mark(also add jump mark to jump table)
            2. convert decoder script level mark to  hardware level control mark.
        """
        pure_control_tokens = []
        for lineno, one_line in dtoken_lines:
            a = []
            for one_dtoken in one_line:
                v = one_dtoken.value
                if one_dtoken.type == dtoken.JUMP_MARK:
                    if self.jump_table.get(v) is not None:
                        raise SyntaxError('duplicate jump label "{}" at line {}'.format(v, lineno))
                    self.jump_table[v] = self.pc
                else:
                    a.append(one_dtoken)

            if len(a) > 0:
                pure_control_tokens.append([lineno, a])
                self.pc_inc()
        return pure_control_tokens

    def compile(self, dtoken_lines):
        self.reset()
        pure_control_tokens = self.split_jump_dtoken(dtoken_lines)
        self.pc = 0

        for lineno, one in pure_control_tokens:
            try:
                self.convert_one_line(one)
                self.pc_inc()
            except SyntaxError as e:
                e.msg = e.msg + " at line " + str(lineno)
                raise e
