from .empty_translator import empty_translator
from ..CTL_LUT import control_LUT
import copy

class ALUTranslator(empty_translator):
    '''
    translate ALU and BUS to ALUS/ALUDL/ALUDH operation.
    ALU meaing using ALU function and  BUS was driverd by ALU.
    ALUO meaing uisng ALU function only, but you still need to check 
    whether there is BUS(ALU) and translate it to BUS(ALUS), BUS(ALUDL) etc.
    '''

    def prepare(self):
        self.type = None

    def get_type_from_parameter(self, p):
        """
        get ALU type according paramter name
        
            p: 
                a paramter
            ret:
                None if not find type, else return type
        """
        if control_LUT.ALUS.have_encoding_name(p):
            return "ALUS"

        if control_LUT.ALUDL.have_encoding_name(p):
            return "ALUDL"

        if control_LUT.ALUDH.have_encoding_name(p):
            return "ALUDH"

        return None

    def scan(self, dt):
        """ decide alu type. """
        if dt.value not in ("ALU", "ALUO"):
            return

        for p in dt.parameters:
            self.type = self.get_type_from_parameter(p)
            if self.type is None:
                continue
            return

        # ALU control but have unknow parameter
        raise SyntaxError(
            'unsupport ALU control for "{}"'.format(dt.simple_str()))

    def translate(self, dt):
        """translate ALU(SOME_FUNTION), BUS(ALU)
        to something lke ALUSD(..),BUS(ALUDH); ALUSD(..),BUS(ALUS); etc..
        """
        if dt.value == "ALUO":
            r = copy.deepcopy(dt)
            r.value = 'ALUSD'
            return r

        if dt.value == "ALU":
            r0 = copy.deepcopy(dt)
            r0.value = 'ALUSD'
            r1 = self.create_bus(dt.lineno, self.type)
            return (r0, r1)

        # "BUS(ALU) -> BUS(ALUS) or BUS(ALUD)"
        if dt.value == "BUS":
            r = copy.deepcopy(dt)
            for idx, p in enumerate(r.parameters):
                if p == "ALU":
                    r.parameters[idx] = self.type
            return r
        return None

