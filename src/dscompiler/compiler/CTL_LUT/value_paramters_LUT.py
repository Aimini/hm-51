
from .abstract_parameters_lut import abstract_parameters_lut


class ValueParametersLUT(abstract_parameters_lut):
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
