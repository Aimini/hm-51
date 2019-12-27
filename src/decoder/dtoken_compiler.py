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

class machine_code:
    def __init__(self):
        # for index i,if self.users[i] is None,
        # it's meaing this bit not used,
        # otherwise it's this bit's user object(dtoken)
        self.value = 0
        self.users = []
    
    def extend_users(self,size):
        """
        ajust user list to target size,append None
            size: 
                target size
        """
        while len(self.users) <= size:
            self.users.append(None)

    def insert(self,value,pos,size,user):
        """
        insert the value to pos, using len of bits, user is used to 
        identify who using the bits.
            value:
                value to insert
            pos:
                start bit position
            size:
                using how many bits
            user:
                who owned those bits
        """
        if value > 2**size:
                raise SyntaxError("encoding value {} to bit to fit size {}".format(value, size))
            
        self.extend_users(pos + size)
        for i in range(size):
            x = i + pos
            if self.users[x] is not None:
                raise SyntaxError("inserted value {} conflict with {}".format(user, self.users[x]))
            self.users[x] = user
        self.value += (value << pos)

class dtoken_compiler:
    def __init__(self, CTL_LUT=control_LUT.CTL_LUT):
        """
        parameter:
            CTL_LUT: 
        """
        self.CTL_LUT = CTL_LUT

    def reset(self):
        self.jump_table = {}  # store jump label address, jump_label:string -> pc_address: int
        # hardware level dtokens, [[lineno,dtoken_list],[lineno,dtoken_list]...]
        self.hl_dtokens = []
        self.rom = []        # store machine code


    def calcuate_LUT_parameters_position(self):
        pos = 0
        for k, v in self.CTL_LUT.items():  # v = RF LUT , WR LUT ...
            pos = v.auto_position(pos)

    def controls_parameters_position_info(self):
        """
        get all control's parameters info
        return: list 
            a list of tuple,
            the tuple contain (pos:int, len:int, name:str)

        """
        pi = []
        for k, v in self.CTL_LUT.items():
            pi.extend([(x[0], x[1], k + '_' + x[2])
                       for x in v.position_info()])
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

    def convert_one_token(self, dt, mc):
        """

        using machine_code object to convert one dtoken to int value
            parameters:
                dt: dtoken
                    dtoken object in current
                mc: machine_code
                    machine_code object used to convert current line
            return: int
                the value of machine_code
        """
        control_parameter_LUTs = self.CTL_LUT.get(dt.value)
        if control_parameter_LUTs is None:
            raise SyntaxError('unkonw control name "{}"'.format(dt.value))

        for i, p in enumerate(dt.parameters):
            place_info, encoding = self.find_parameter_encoding_info(
                i, p, control_parameter_LUTs)

            if place_info is None:
                raise SyntaxError('unkonw control parameter "{}"'.format(p))

            # jump mark in address, etc.
            if not isinstance(encoding, int):
                encoding = self.jump_table.get(encoding)

            if not isinstance(encoding, int):
                print(dt)
                raise SyntaxError('unkonw control parameter "{}"'.format(p))
            
            mc.insert(encoding,place_info[0],place_info[1], dt)

    def convert_one_line(self, dtokens):
        """
        convert one lines token to machine code
            return: int
                current line machine code value
        """
        mc = machine_code()
        for one in dtokens:
            self.convert_one_token(one, mc)
        return mc.value

    def split_jump_dtoken(self, dtoken_lines):
        """
            generate pure control dtokens
            1. remove jump mark(also build jump table)
            2. move pure control dtokens to new list
        """
        pure_control_tokens = []
        pc = 0
        for lineno, one_line in dtoken_lines:
            a = []
            for one_dtoken in one_line:
                v = one_dtoken.value
                # check jump mark
                if one_dtoken.type == dtoken.JUMP_MARK:
                    if self.jump_table.get(v) is not None:
                        raise SyntaxError(
                            'duplicate jump label "{}" at line {}'.format(v, lineno))
                    self.jump_table[v] = pc
                else:
                    a.append(one_dtoken)
            # if this line contain control mark
            if len(a) > 0:
                pure_control_tokens.append([lineno, a])
                pc += 1
        return pure_control_tokens

    def compile(self, dtoken_lines):
        """
        convert dtokens lines to machine code list
            dtoken_lines: list
            a list return from dtoken_converters.convert
                [
                    [lineno, [dtokens,dtokens...]],
                    [lineno, [dtokens,dtokens...]],
                    [lineno, [dtokens,dtokens...]],
                    ...
                ]        

            return: list[int]
                a list of final machine code value
                [v0:int, v1:int, ...]

        """
        self.reset()
        pure_control_tokens = self.split_jump_dtoken(dtoken_lines)

        machine_code_lines = []
        for lineno, one in pure_control_tokens:
            try:
                machine_code_lines.append(self.convert_one_line(one))
            except SyntaxError as e:
                e.msg = e.msg + " at line " + str(lineno)
                raise e
        return machine_code_lines
