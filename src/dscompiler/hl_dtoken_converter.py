##########################################
#   AI
#   2019-12-26 14:08:16
# class hl_dtoken_converter:
#  Translate programmer friendly dtokens into hardware-level dtokens
#       RF(WE) -> RF(LWE, HWE)
#       IMMED(0xFF)  -> JUMP(0xFF,0), BUS(IMMED)
#
#  class *_translator:
#   do translate work
#   when hl_dtoken_converter prepare to scan a line of of dtokens
#   it's will invoke translator.prepare
#   when hl_dtoken_converter first scan the line, it will call translator.scan1
#   you can get inform about this line in this method.
#   when hl_dtoken_converter second scan the same line of dtokens, it's call translator.scan2,
#   you will translate the dtoken to target dtoken(s) and return a list of target dtokens.
##########################################
import dtoken
import control_LUT
import copy


class empty_translator():
    """
    a translator than do nothing, providing create dtoken function.
    """

    def prepare(self):
            pass

    def scan(self, dt):
        """
        you can get info from dtokens in current line.
            dt: dtoken
        """
        pass

    def translate(self, dt):
        """
        after scan, you might translate some dtoken to other dtokens.
        If return None, meaing using origin dtoken, else using dtokens that you returned.
            dt: dtoken
                dtoken might be translated.
        """

        return None

    def create_jump(self, lineno, type):
        r = dtoken.dtoken(lineno, dtoken.PAR_CONTROL, "JUMPABS")
        r.parameters = [type]
        return r

    def create_address(self, lineno, addr):
        r = dtoken.dtoken(lineno, dtoken.PAR_CONTROL, "ADDRESS")
        r.parameters = [addr]
        return r

    def create_immed(self, lineno, value):
        r = dtoken.dtoken(lineno, dtoken.PAR_CONTROL, "IMMED")
        r.parameters = [value]
        return r

    def create_bus(self, lineno, sel):
        r = dtoken.dtoken(lineno, dtoken.PAR_CONTROL, "BUS")
        r.parameters = [sel]
        return r


class alu_translator(empty_translator):
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


class rf_translator(empty_translator):
    """
    translate RF(WE,...) to RF(HWE,LWE,...)
    """

    def translate(self, dt):
        """
            second scan, if you decide to translate dtoken to another dtoken
            return a not None object(dtoken or dtoken list).
        """
        if dt.value != "RF":
            return None

        r = copy.deepcopy(dt)
        for idx, p in enumerate(r.parameters):
            if p == "WE":
                r.parameters[idx] = "HWE"
                r.parameters.insert(idx, "LWE")
        return r


class jump_translator(empty_translator):
    def translate(self, dt):
        r = []
        if dt.value not in ("J", "JLT", "JGT", "JBIT", "JRST"):
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


class load_immed_translator(empty_translator):
    def translate(self, dt):

        if dt.value != "LI":
            return None

        r = []
        r.append(self.create_immed(dt.lineno, dt.parameters[0]))
        r.append(self.create_bus(dt.lineno, "IMMED"))
        return r


DEFAULT_TRANSLATOR = (alu_translator(), 
                      jump_translator(), load_immed_translator())


class hl_dtoken_converter:
    def __init__(self, dtoken_translators=DEFAULT_TRANSLATOR):
        self.dtokens_translator = dtoken_translators

    def convert(self, dtoken_lines):
        """
            generate hardware level dtoken that will convert to machine code.

            dtoken_lines: list
                a list from dtoken_converter.convert
                [
                    [lineno:int, [dtoken00_at_this_line(dtoken), dtoken01_at_this_line(dtoken), ..]]
                    [lineno:int, [dtoken10_at_this_line(dtoken), dtoken11_at_this_line(dtoken), ..]]
                    ...
                ]

            ret: list
                a list have same organization of input list

        """
        hl_dtokens = []
        for lineno, one_line in dtoken_lines:
            a = []
            try:
                # prepare
                for one_translator in self.dtokens_translator:
                    one_translator.prepare()

                #first scan
                for one_dtoken in one_line:
                    for one_translator in self.dtokens_translator:
                        one_translator.scan(one_dtoken)

                #second scan
                for one_dtoken in one_line:
                    translated = False
                    for one_translator in self.dtokens_translator:
                        r = one_translator.translate(one_dtoken)

                        # translated
                        if r is not None:
                            translated = True
                            if isinstance(r, (tuple, list)):
                                a.extend(r)
                            else:
                                a.append(r)
                            break

                    # append raw dtoken
                    if not translated:
                        a.append(one_dtoken)

                # not a empty line
                if len(a) > 0:
                    hl_dtokens.append([lineno, a])

            except SyntaxError as e:
                e.msg += " at line " + str(lineno)
                raise e
        return hl_dtokens
