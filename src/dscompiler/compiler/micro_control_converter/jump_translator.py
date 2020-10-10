from .empty_translator import empty_translator
from ..CTL_LUT.control_LUT import JUMPABS
class JumpTranslator(empty_translator):
    def translate(self, dt):
        r = []
        if not JUMPABS.have_encoding_name(dt.value):
            return None

        lineno = dt.lineno
        jump_token = self.create_jump(lineno, dt.value)
        r.append(jump_token)

        p0 = "" if len(dt.parameters) < 1 else dt.parameters[0]
        p1 = "" if len(dt.parameters) < 2 else dt.parameters[1]
        if dt.value in ("J", "JBIT", "JALUF"):

            addr_token = self.create_address(lineno, p0)
        else:
            addr_token = self.create_address(lineno, p1)
            immed_token = self.create_immed(lineno, p0)
            r.append(immed_token)
        r.append(addr_token)

        return r