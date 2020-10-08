
from .empty_translator import empty_translator

class LoadImmedTranslator(empty_translator):
    def translate(self, dt):

        if dt.value != "LI":
            return None

        r = []
        r.append(self.create_immed(dt.lineno, dt.parameters[0]))
        r.append(self.create_bus(dt.lineno, "IMMED"))
        return r
