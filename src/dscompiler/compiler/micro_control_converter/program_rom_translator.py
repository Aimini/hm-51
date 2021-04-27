
from .empty_translator import empty_translator

class PROMTranslator(empty_translator):
    def translate(self, dt):

        if dt.value != "PRR":
            return None

        r = []
        # ACTIVE, ~CE, WE is reused from IMMED[0:2]
        # ACTIVE bit will be set by default
        immed = 0x3 # buffer's direction is always from data bus to ROM
                     # ~CE deafults to high(deactive)
                     # WE defaults to low
        for p in dt.parameters:
            if p == "CE":
                immed ^= 0x2
            elif p == "WE":
                immed |= 0x4
                
        r.append(self.create_immed(dt.lineno, immed))
        r.append(self.create_loadprr(dt.lineno))
        return r
