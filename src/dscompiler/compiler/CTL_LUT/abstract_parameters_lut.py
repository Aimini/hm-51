
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

    def inital_value(self):
        return 0