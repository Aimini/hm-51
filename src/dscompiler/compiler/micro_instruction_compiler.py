##################################################################
# 2019-12-22 12:44:23
# AI
# dtoken compiler, compile all dtoken in all lines to physical-level
# machine code, we can treat a part of circuit as a component that
# have multiple input controls.
# for example:
# RF(Register File) have three function input:
#   source select, write low and write high
# then we can using mark "LWE" to meaing write low, "A" meaing select
# reigiter 0 in RF.
#
# for moest of parameter control mark, it's only using name parameter,
# we can just using a LUT to find encoding parameter encoding.
# for another control mark, we using special logic to encode it.
###############################################################
import enum

from . import micro_control
from .CTL_LUT.named_parameters_lut import NamedParametersLUT
from .CTL_LUT.value_paramters_LUT import ValueParametersLUT
from .CTL_LUT.control_LUT import DEFAULT_CTL_LUT

class machine_code:
    '''
    provide mechanism to insert value to target bit index with excepted bit-len
    it's provide protective measures to prevent accident mistake:
    - Checks if the inserted value fits the length of the target bit (prevents truncate)
    - Checks whether inserted value will overlaps with the bits than had encoded other values
    '''

    def __init__(self,bits_len,initial_value):
        #because some pin are active low, it's default state should be 1,
        #  so we need initial value
        self.bits_len = bits_len
        self.value = initial_value
        # for index i,if self.users[i] is None,
        # it's meaing this bit not used,
        # otherwise it's this bit's user object(dtoken)
        self.users = [None for _ in range(bits_len)]
        


    def insert(self, value, pos, size, user):
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

        if value > 2**size or value < 0:
                raise SyntaxError("encoding value {} to bit to fit size {}".format(value, size))

        for i in range(size):
            x = i + pos
            if self.users[x] is not None:
                raise SyntaxError("inserted value {} conflict with {}".format(user, self.users[x]))
            if (1 << x) & self.value:
                self.value ^= (1 << x)
            self.users[x] = user
            
        self.value |= (value << pos)


class MicroinstrcutionCompiler:
    def __init__(self, CTL_LUT = DEFAULT_CTL_LUT):
        """
        parameter:
            CTL_LUT: see control_LUT.CTL_LUT
        """
        self.CTL_LUT = DEFAULT_CTL_LUT

    def reset(self):
        self.jump_table = {}  # store jump label address, jump_label:string -> pc_address: int
        # hardware level dtokens, [[lineno,dtoken_list],[lineno,dtoken_list]...]
        self.hl_dtokens = []

    def calcuate_LUT_parameters_position(self):
        pos = 0
        self.inital_machine_code = 0
        for k, v in self.CTL_LUT.items():  # v = RF LUT , WR LUT ...
            pos = v.auto_position(pos)
        self.bits_len = pos
        self.bytes_len = int((self.bits_len + 7)/8)

        self.inital_machine_code = 0
        for k, v in self.CTL_LUT.items():  # v = RF LUT , WR LUT ...
            for par in v.LUT:
                if par.get('al',False):
                    pos,l= par['pos'], par['len']
                    self.inital_machine_code |= ((2**l - 1) << pos)


        
    def controls_parameters_position_info(self):
        """
        get all control's parameters info
            return: list 
                a list of tuple contain (pos:int, len:int, name:str)

        """
        pi = []
        # iterate each control's LUT
        for k, v in self.CTL_LUT.items():
            pi.extend([(x[0], x[1], k + '_' + x[2])
                       for x in v.position_info()])
        return pi

    def convert_mcrio_controls(self, dt, mc):
        """
        using machine_code object to convert one dtoken to int value
            parameters:
                dt: dtoken
                    dtoken object in current line
                mc: machine_code
                    machine_code object used to convert current line
            return: int
                the value of machine_code
        """
        control_parameter_LUTs = self.CTL_LUT.get(dt.value)
        if control_parameter_LUTs is None:
            raise SyntaxError('unkonw control name "{}"'.format(dt.value))

        for i, p in enumerate(dt.parameters):
            if isinstance(control_parameter_LUTs, NamedParametersLUT):
                place_info, encoding = control_parameter_LUTs.get_info(p)
            elif isinstance(control_parameter_LUTs, ValueParametersLUT):
                place_info = control_parameter_LUTs.get_place_info(i)
                if isinstance(p, int):
                    encoding = p
                else:
                    encoding = self.jump_table.get(p)
                    #for dissasemble, replace string mark to number
                    dt.parameters[i] = encoding
            
            if place_info is None:
                raise SyntaxError('unkonw control parameter "{}"'.format(p))

            if not isinstance(encoding, int):
                raise SyntaxError('unkonw control parameter "{}"'.format(p))

            mc.insert(encoding, place_info[0], place_info[1], dt)

    def convert_one_line(self, dtokens):
        """
        convert one lines token to machine code
            return: int
                current line machine code value
        """
        mc = machine_code(self.bits_len, self.inital_machine_code)  
        for one in dtokens:
            self.convert_mcrio_controls(one, mc)
        return mc.value

    def split_jump_control(self, dtoken_lines):
        """
        generate pure control dtokens
        1. remove jump mark(also build jump table)
        2. move pure control dtokens to new list

            dtoken_lines: list
                a list return from hl_dtoken_converters.convert
                [
                    [lineno, [dtokens,dtokens...]],
                    [lineno, [dtokens,dtokens...]],
                    [lineno, [dtokens,dtokens...]],
                    ...
                ]
        """
        pure_control_tokens = []
        pc = 0

        for lineno, one_line in dtoken_lines:
            a = []
            for one_dtoken in one_line:
                v = one_dtoken.value

                # check jump mark
                if one_dtoken.type == micro_control.JUMP_MARK:
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
                a list return from hl_dtoken_converters.convert
                [
                    [lineno, [dtokens,dtokens...]],
                    [lineno, [dtokens,dtokens...]],
                    [lineno, [dtokens,dtokens...]],
                    ...
                ]

            ret: (list,list)
                ret[0] is a list of final machine code value.
                [
                    [lineno:int, code:int],
                    [lineno:int, code:int],
                    ...
                ]

                ret[1] is a list of pure control dtoken list.
                [
                    [lineno:int, [dtoken,dtoken,...]],
                    [lineno:int, [dtoken,dtoken,...]],
                    ...
                ]

                lineno is line number in source .ds file
        """
        self.reset()
        pure_micro_instructions = self.split_jump_control(dtoken_lines)

        machine_code_lines = []
        for lineno, one in pure_micro_instructions:
            try:
                code = self.convert_one_line(one)
                machine_code_lines.append([lineno, code, one])
            except SyntaxError as e:
                e.msg = e.msg + " at line " + str(lineno)
                raise e
        return machine_code_lines, pure_micro_instructions
