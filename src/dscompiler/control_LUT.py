
###########################################################
# parmater name encoding LUT
# for one component(RF, WR, SR or other component), we have
# LUT organized like below:

###########################################################

# register file control label encoding

#
import copy


class abstract_parameters_lut():
    def __init__(self, LUT):
        self.LUT = LUT

    def auto_position(self, start):
        """
        Automatically assign the start position of each parameter
            start:int
                The position of the first bit to allocate
        """
        pos = start
        for one in self.LUT:
            one['pos'] = pos
            pos += one['len']
        return pos

    def position_info(self):
        """
        return parameters position info.
            return:
                tuple:(pos:int , len:int ,name:str)
        """
        r = []
        for one in self.LUT:
            r.append((one['pos'], one['len'], one['sh']))
        return r


class name_parameters_lut(abstract_parameters_lut):
    """
    using string name to find encoding
    """

    def __init__(self, LUT):
        """
        LUT:list
            [
                {
                    'sh': 'short hand',
                    'name': 'full name',
                    'len' : 'bit length to encoding',
                    'pos' : 'start position to encoding',
                    'enum' : ['NAME0','NAME1',...]
                },
                {
                    'sh': 'short hand',
                    'name': 'full name',
                    ...  # same as above map
                },
                ... # same as above map
            ]
        """
        super().__init__(LUT)
        self.LUT = LUT

    def try_enum_multiname_encoding(self, multiname_list, parameter_name):
        """
        treat current enum as a list contain multiple name, and try find
        parameter_name in this list.
            ret:bool
                True is find name else return False
        """
        if isinstance(multiname_list, (tuple, list)):
            try:
                multiname_list.index(parameter_name)
                return True
            except ValueError:
                return False
        else:
            return False

    def get_info(self, parameter_name):
        '''
        get parameter's enum name ecoding and place info
            parameter_name: str
            return: Tuple
                (place_info:Tuple,encoding:int)
                    place_info:
                    (pos:int, len:int)
        '''
        idx, encoding = self.get_encoding(parameter_name)
        if idx is None:
            return None, None
        else:
            one = self.LUT[idx]
            place_info = (one['pos'], one['len'])
            return place_info, encoding

    def get_encoding(self, name):
        """
        get a name encoding info:
        return:
            index, encoding
            self.LUT[index] is the parameter LUT that cantain the name in it's enum list
        """
        for idx, one in enumerate(self.LUT):
            # find parameter name in one parameter LUT
            for encoding, enum_name in enumerate(one['enum']):
                if name == enum_name:
                    return idx, encoding

                if self.try_enum_multiname_encoding(enum_name, name):
                    return idx, encoding

        return None, None

    def have_encoding_name(self, name):
        idx, _ = self.get_encoding(name)
        return idx != None


class value_parameter_lut(abstract_parameters_lut):
    def __init__(self, LUT):
        super().__init__(LUT)
        self.LUT = LUT

    def get_place_info(self, i):
        '''
        get parameter's enum name ecoding and place info
        return:
            place_info : (pos:int, len:int)
        '''
        one = self.LUT[i]
        # find parameter name in one parameter LUST
        return (one['pos'], one['len'])


# one control have many parameters,
# one parameter have many avaliable enum name
# one encoding  enum name
REGISTER_FILE = name_parameters_lut([
    {
        'sh': 'SRC',
        'name': 'register selector',
        'len': 4,
        'enum': ['SP',  'DPL', 'DPH', 'IE',
                 'IP',  'PSW', 'A',   'B',
                 'PCL', 'PCH', 'IR',  'ISR',
                 'T0',  'T1',  'T2',  'T3']
    },
    {
        'sh': 'WE',
        'name': 'write low nibble',
        'len': 1,
        'enum': ['', 'WE']
    },
    {
        'sh': 'SFR',
        'name': 'let SFR mechanism control it',
        'len': 1,
        'enum': ['', 'SFR']
    }
])

BUS = name_parameters_lut([
    {
        'sh': 'SRC',
        'name': 'bus ouput driver',
        'len': 3,
        'enum': ['ALUS', 'ALUDL', 'ALUDH', 'IMMED', 'RAM', 'XRAM', 'ROM', 'IRQ']
    }
])

WR = name_parameters_lut([
    {
        'sh': 'WE',
        'name': 'write enable',
        'len': 1,
        'enum': ['', 'WE']
    }
])

SR = name_parameters_lut([
    {
        'sh': 'WE',
        'name': 'write enable',
        'len': 1,
        'enum': ['', 'WE']
    }
])

RFSRCR = name_parameters_lut([
    {
        'sh': 'WE',
        'name': 'write enable',
        'len': 1,
        'enum': ['', "WE"],
    }
])
BR = name_parameters_lut([
    {
        'sh': 'SRC',
        'name': 'input select',
        'len': 3,
        'enum': ['Q', 'NQ', 'ZERO', 'ONE',
                 'ALUSF', ['ALUDF', 'CY', 'ZF', 'PF'], 'A7', 'A0'],
    },
    {
        'sh': 'CPLQ',
        'name': 'invert output',
        'len': 1,
        'enum': ['', 'CPLQ'],
    }
])


RAM = name_parameters_lut([
    {
        'sh': 'WE',
        'name': 'write enable',
        'len': 1,
        'enum': ['', 'WE']
    }
])

XRAM = name_parameters_lut([
    {
        'sh': 'WE',
        'name': 'write enable',
        'len': 1,
        'enum': ['', 'WE']
    }
])
####################################################################
# see /src/alu/README.md get more info about ALU function info
####################################################################
ALUDL = name_parameters_lut([
    {
        'sh': 'FUNC',
        'name': 'alud low part function',
        'len': 4,
        'enum': [
            'XOR', 'DA', 'ADDC', 'SUBB',
            'A',  'B', 'INSB', 'XCHD',
            'GENIRQN', 'SETPSWF', 'ADDR11REPLACE', 'SETOVCLRCY',
            'Ri', 'Rn', 'SETPF', 'INCC']
    }
])
# see /src/alu/README.md
ALUDH = name_parameters_lut([
    {
        'sh': 'FUNC',
        'name': 'alud high part function',
        'len': 4,
        'enum': [
            '',   'DAF', 'ADDCF', 'SUBBF',
            'PF', 'ZF',  'INSBF',  'EXTB',
            'ISRAPPIRQ',   '',    '',      '',
            'OR',    'AND',   'NA', 'INCCF']
    }
])

# see /src/alu/README.md
ALUS = name_parameters_lut([
    {
        'sh': 'FUNC',
        'name': 'alus function',
        'len': 4,
        'enum':  ['ADJF', 'IVADDR', 'CAA', 'SFR',
                  'RR', 'RL', 'RRC', 'RLC',
                  'INC', 'DEC', 'BADDR', 'BIDX',
                  'SETCY', 'SELHIRQ', 'ISRRETI', 'SWAP']
    }
])


def copy_one_parameter(dest, src):
    dest_enum = dest["enum"]
    src_enum = src["enum"]
    for idx, value in enumerate(dest_enum):
        if idx >= len(src_enum):
            break

        vr = dest_enum[idx]
        va = src_enum[idx]

        if isinstance(vr, (list, tuple)):
            a = vr
        else:
            a = [vr]

        if isinstance(va, (list, tuple)):
            a.extend(va)
        else:
            a.append(va)

        dest_enum[idx] = a


ALUSD = name_parameters_lut(copy.deepcopy(ALUS.LUT))
for idx, one in enumerate(ALUSD.LUT):
    copy_one_parameter(one, ALUDL.LUT[idx])
    copy_one_parameter(one, ALUDH.LUT[idx])

IRQ = name_parameters_lut([
    {
        'sh': '',
        'name': 'write enable',
        'len': 1,
        'enum': ['', 'CLR']
    }
])

JUMPABS = name_parameters_lut([
    {
        'sh': 'TYPE',
        'name': 'jump type',
        'len': 3,
        'enum':  ['', 'J', 'JGT', 'JEQ',
                  'JLT', 'JBIT', 'JRST', '']
    }
])

ADDRESS = value_parameter_lut([
    {

        'sh': '',
        "name": "target address",
        "len": 12
    }
])

IMMED = value_parameter_lut([
    {

        'sh': '',
        "name": "a byte of immediate value",
        "len": 8
    }
])

##################
# each control's parmaters LUT to make a big control LUT
CTL_LUT = {
    'RF': REGISTER_FILE,
    'BUS': BUS,
    'WR': WR,
    'SR': SR,
    'BR': BR,
    'RFSRCR': RFSRCR,
    'RAM': RAM,
    'XRAM': XRAM,
    'ALUSD': ALUSD,
    'IRQ': IRQ,
    'JUMPABS': JUMPABS,
    'ADDRESS': ADDRESS,
    'IMMED': IMMED,
}
