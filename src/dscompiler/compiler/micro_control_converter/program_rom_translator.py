
from .empty_translator import empty_translator

class PROMTranslator(empty_translator):
    def translate(self, dt):

        if dt.value != "PROROM":
            return None

        r = []
        # CE,OE,WE, BUFDIR is reused from IMMED[0:3]
        immed = 0xF # buffer's direction is always from data bus to ROM
                     # CE OE WE deafults to high(deactive)
        for p in dt.parameters:
            if p == "CE":
                immed ^= 0x4
            elif p == "OE":
                immed ^ 0x2
            elif p == "WE":
                immed ^= 0x4
                
        r.append(self.create_immed(dt.lineno, immed))
        r.append(self.create_prom(dt.lineno))
        return r
