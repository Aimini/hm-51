
from .abstract_parameters_lut import abstract_parameters_lut

class NamedParametersLUT(abstract_parameters_lut):
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
            if one.get('al',False):
                encoding = (2**one['len'] - 1) ^ encoding
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