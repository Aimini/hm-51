
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
    def __init__(self, LUT):
        super().__init__(LUT)
        self.LUT = LUT

    def try_enum_multiname_encoding(self, multiname_list, parameter_name):
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
        return:
            (place_info:Tuple,encoding:int)
            place_info : (pos:int, len:int)
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
            # find parameter name in one parameter LUST
            for encoding, enum_name in enumerate(one['enum']):
                if self.try_enum_multiname_encoding(enum_name, name):
                    return idx, encoding

                if name == enum_name:
                    return idx, encoding
        return None, None

    def have_encoding_name(self, name):
        idx, encoding = self.get_encoding(name)
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
        'enum': ['A',   'B',  'SP', 'PSW',
                 'DPL', 'DPH', 'IE', 'IP',
                 'PCL', 'PCH', 'IR', 'ISR',
                 'T0', 'T1',  'T2',  'T3']
    },
    {
        'sh': 'LWE',
        'name': 'write low nibble',
        'len': 1,
        'enum': ['', 'LWE']
    },
    {
        'sh': 'HWE',
        'name': 'write high nibble',
        'len': 1,
        'enum': ['', 'HWE']
    }
])

BUS = name_parameters_lut([
    {
        'sh': 'SRC',
        'name': 'bus ouput driver',
        'len': 3,
        'enum': ['Z', 'ALUS', 'ALUD', 'IMMED', 'RAM', 'XRAM', 'ROM', 'IRQ']
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


BR = name_parameters_lut([
    {
        'sh': 'SRC',
        'name': 'input select',
        'len': 3,
        'enum': ['Q', 'NQ', 'ZERO', 'ONE',
                 'ALUSF', ['ALUDF', 'CY', 'ZF', 'PF'], 'A7', 'A0'],
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

ALUD = name_parameters_lut([
    {
        'sh': 'FUNC',
        'name': 'alud function',
        'len': 4,
        'enum': [
            ['ORL', 'PF'], ['ANL', 'ZF'], 'XRL', 'B',
            'ADD',  'ADDC', 'SUBB', 'DA',
            'SHIRQN', 'IRQN2IRQ', 'EXTB', 'INSB',
            'ADDR11REPLACE', 'SETPSWF', 'Ri', 'Rn']
    }
])

ALUS = name_parameters_lut([
    {
        'sh': 'FUNC',
        'name': 'alus function',
        'len': 4,
        'enum':  ['A', 'NOTA', 'CAA', 'SETPF',
                  'RR', 'RL', 'RRC', 'RLC',
                  'INC', 'DEC', 'BADDR', 'BIDX',
                  'SSETCY', 'SETOVCLRCY', 'CHIRQ', 'SWAP']
    }
])


def copy_one_parameter(dest, src):
    dest_enum = dest["enum"]
    src_enum = src["enum"]
    for idx, value in enumerate(dest_enum):
        if idx >= len(dest_enum):
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


ALUSD = name_parameters_lut(copy.deepcopy(ALUD.LUT))
for idx, one in enumerate(ALUSD.LUT):
    copy_one_parameter(one, ALUS.LUT[idx])

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
    'RAM': RAM,
    'ALUSD': ALUSD,
    'JUMPABS': JUMPABS,
    'ADDRESS': ADDRESS,
    'IMMED': IMMED,
}
