
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

#


class name_parameters_lut:
    def __init__(self, LUT):
        self.LUT = LUT

    def try_enum_multiname_encoding(self, multiname_list, parameter_name):
        if isinstance(multiname_list,(tuple,list)):
            multiname_list.index(parameter_name)
            return True
        else:
            return False

    def get_info(self, parameter_name):
        '''
        get parameter's enum name ecoding and place info
        return:
            (place_info:Tuple,encoding:int)
            place_info : (pos:int, len:int)
        '''
        for one in self.LUT:
            # find parameter name in one parameter LUST
            place_info = (one['pos'], one['len'])
            for encoding, enum_name in enumerate(one['enum']):
                if self.try_enum_multiname_encoding(enum_name, parameter_name):
                    return place_info, encoding

                if parameter_name == enum_name:
                    return place_info, encoding
        return None,None

    def auto_position(self, start):
        pos = start
        for one in self.LUT:
            one['pos'] = pos
            pos += one['len']
        return pos


# one control have many parameters,
# one parameter have many avaliable enum name
# one encoding  enum name
REGISTER_FILE = name_parameters_lut([
    {
        'name': 'register selector',
        'len': 4,
        'enum': ['A',   'B',  'SP', 'PSW',
                 'DPL', 'DPH', 'IE', 'IP',
                 'PCL', 'PCH', 'IR', 'T0',
                 'T1',  'T2',  'T3']
    },
    {
        'name': 'write low nibble',
        'len': 1,
        'enum': ['', 'LWE']
    },
    {
        'name': 'write high nibble',
        'len': 1,
        'enum': ['', 'HWE']
    }
])

BUS = name_parameters_lut([
    {
        'name': 'bus ouput driver',
        'len': 3,
        'enum': ['Z', 'ALUS', 'ALUD', 'IMMED', 'RAM', 'XRAM', 'ROM', 'IRQ']
    }
])

WR = name_parameters_lut([
    {
        'name': 'write enable',
        'len': 1,
        'enum': ['', 'WE']
    }
])

SR = name_parameters_lut([
    {
        'name': 'write enable',
        'len': 1,
        'enum': ['', 'WE']
    }
])


BR = name_parameters_lut([
    {
        'name': 'input select',
        'len': 3,
        'enum': ['Q', 'NQ', '0', '1', 'ALUSF', 'ALUDF', 'A7', 'A0'],
    }
])
ALUD = name_parameters_lut([
    {
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
        'name': 'alus function',
        'len': 4,
        'enum':  ['A', 'NOTA', 'CAA', 'SETPF',
                  'RR', 'RL', 'RRC', 'RLC',
                  'INC', 'DEC', 'BADDR', 'BIDX',
                  'SSETCY', 'SETOVCLRCY', 'CHIRQ', 'SWAP']
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
    'ALUS': ALUS,
    'ALUD': ALUD,
}


    ### jump encode
    ### jump using position to encode parameter value
JUMP_LUT=[
    [[3], ['_NJUMP', 'JMP', 'JLT', 'JGT', 'JEQ', 'JBIT', '', '']],  # jump type encode
    # control parameters len
    # addres, simmed
    [[13],   [8]]
]
