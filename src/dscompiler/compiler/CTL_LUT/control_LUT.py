
###########################################################
# parmater name encoding LUT
# for one component(RF, WR, SR or other component), we have
# LUT organized like below:

###########################################################

# register file control label encoding

#
import copy
from .named_parameters_lut import NamedParametersLUT
from .value_paramters_LUT import ValueParametersLUT


# one control have many parameters,
# one parameter have many avaliable enum name
# one encoding  enum name
REGISTER_FILE = NamedParametersLUT([
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

BUS = NamedParametersLUT([
    {
        'sh': 'SRC',
        'name': 'bus ouput driver',
        'len': 3,
        'enum': ['ALUS', 'ALUDL', 'ALUDH', 'RAM', 'ROM',  'XRAM', 'IMMED', 'IRR']
    }
])

WR = NamedParametersLUT([
    {
        'sh': 'WE',
        'name': 'write enable',
        'len': 1,
        'al': True,
        'enum': ['', 'WE']
    }
])

SR = NamedParametersLUT([
    {
        'sh': 'WE',
        'name': 'write enable',
        'len': 1,
        'al': True,
        'enum': ['', 'WE']
    }
])

RFSRCR = NamedParametersLUT([
    {
        'sh': 'WE',
        'name': 'write enable',
        'len': 1,
        'al': True,
        'enum': ['', "WE"],
    },
    {
        'sh': '__1',
        'name': 'just for algin 8 bit for control relative to RF',
        'len': 1,
        'al': False,
        'enum': ['AFASFASFAFF', "GGGGGGGGGGGGGG"],
    }
])
BR = NamedParametersLUT([
    {
        'sh': 'SRC',
        'name': 'input select',
        'len': 3,
        'enum': ['Q', 'NQ', 'ZERO', 'ONE',
                 "ALUDNF", ['ALUDF', 'CY', 'ZF', 'PF'],  'A0', 'A7'],
    },
    {
        'sh': 'CPLQ',
        'name': 'invert output',
        'len': 1,
        'enum': ['', 'CPLQ'],
    }
])


RAM = NamedParametersLUT([
    {
        'sh': 'WE',
        'name': 'write enable',
        'len': 1,
        'enum': ['', 'WE']
    }
])

XRAM = NamedParametersLUT([
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
ALUDL = NamedParametersLUT([
    {
        'sh': 'FUNC',
        'name': 'alud low part function',
        'len': 4,
        'enum': [
            'XOR', 'DA', 'ADDC', 'SUBB',
            'A',  'Ri', 'INSB', 'XCHD',
            'GENIRRQN', 'SETPSWF', 'ADDR11REPLACE', 'SETOVCLRCY',
            'B', 'Rn', 'SETPF', 'INCC']
    }
])
# see /src/alu/README.md
ALUDH = NamedParametersLUT([
    {
        'sh': 'FUNC',
        'name': 'alud high part function',
        'len': 4,
        'enum': [
            'CPLB', 'DAF', 'ADDCF', 'SUBBF',
            'PF', 'OR',  'INSBF',  'EXTB',
            'ISRSET',   'ZF',    '',      '',
            'ZF_B',    'AND',   'NA', 'INCCF']
    }
])

# see /src/alu/README.md
ALUS = NamedParametersLUT([
    {
        'sh': 'FUNC',
        'name': 'alus function',
        'len': 4,
        'enum':  ['ADJF', 'IVADDR', 'CAA', 'SFR',
                  'RR', 'RL', 'RRC', 'RLC',
                  'INC', 'DEC', 'BADDR', 'BIDX',
                  'SETCY', 'SELHIRRQN', 'ISRRETI', 'SWAP']
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


ALUSD = NamedParametersLUT(copy.deepcopy(ALUS.LUT))
for idx, one in enumerate(ALUSD.LUT):
    copy_one_parameter(one, ALUDL.LUT[idx])
    copy_one_parameter(one, ALUDH.LUT[idx])

IRR = NamedParametersLUT([
    {
        'sh': 'CAI',
        'name': 'write enable',
        'len': 1,
        'enum': ['', 'CLR']
    }
])

JUMPABS = NamedParametersLUT([
    {
        'sh': 'TYPE',
        'name': 'jump type',
        'len': 3,
        'enum':  ['', 'J', 'JGT', 'JEQ',
                  'JLT', 'JALUNF', 'JALUF', 'JBIT']
    }
])

ADDRESS = ValueParametersLUT([
    {

        'sh': '',
        "name": "target address",
        "len": 12
    }
])

IMMED = ValueParametersLUT([
    {

        'sh': '',
        "name": "a byte of immediate value",
        "len": 8
    }
])

MIPCSRC = NamedParametersLUT([
    {
        'sh': 'MIPCSRC',
        'name': 'MIPC data source',
        'len': 1,
        'enum':  ['', 'DECVEC']
    }
])


##################
# each control's parmaters LUT to make a big control LUT
DEFAULT_CTL_LUT = {
    'IMMED': IMMED,
    'ADDRESS': ADDRESS,
    'JUMPABS': JUMPABS,
    'MIPCSRC': MIPCSRC,
    'RF': REGISTER_FILE,
    'RFSRCR': RFSRCR,
    'SR': SR,
    'RAM': RAM,
    'XRAM': XRAM,
    'BR': BR,
    'WR': WR,
    'ALUSD': ALUSD,
    'BUS': BUS,
    'IRR': IRR,
}
