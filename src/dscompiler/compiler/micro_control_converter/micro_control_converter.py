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
from .alu_translator import ALUTranslator
from .jump_translator import JumpTranslator
from .load_immed_translator import LoadImmedTranslator

DEFAULT_TRANSLATOR = (ALUTranslator(), 
                      JumpTranslator(), LoadImmedTranslator())





class MicroControlConverter:
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
