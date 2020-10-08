from .empty_translator import empty_translator

class JumpTranslator(empty_translator):
    def translate(self, dt):
        r = []
        if dt.value not in ("J", "JLT","JEQ", "JGT", "JBIT", "JRST"):
            return None

        lineno = dt.lineno
        jump_token = self.create_jump(lineno, dt.value)
        r.append(jump_token)

        p0 = "" if len(dt.parameters) < 1 else dt.parameters[0]
        p1 = "" if len(dt.parameters) < 2 else dt.parameters[1]
        if dt.value in ("J", "JBIT", "JRST"):

            addr_token = self.create_address(lineno, p0)
        else:
            addr_token = self.create_address(lineno, p1)
            immed_token = self.create_immed(lineno, p0)
            r.append(immed_token)
        r.append(addr_token)

        return r