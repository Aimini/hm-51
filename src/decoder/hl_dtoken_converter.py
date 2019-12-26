##########################################
#   AI
#   2019-12-26 14:08:16
# class hl_dtoken_converter:
#  Translate programmer friendly dtokens into hardware-level dtokens
#       RF(WE) -> RF(LWE, HWE)
#       IMMED(0xFF)  -> JUMP(0xFF,0), BUS(IMMED)
#
#  class *_translater:
#   do translate work
#   when hl_dtoken_converter prepare to scan a line of of dtokens
#   it's will invoke translater.prepare
#   when hl_dtoken_converter first scan the line, it will call translater.scan1
#   you can get inform about this line in this method.
#   when hl_dtoken_converter second scan the same line of dtokens, it's call translater.scan2,
#   you will translate the dtoken to target dtoken(s) and return a list of target dtokens.
##########################################
import dtoken
import control_LUT
import copy
class alu_translater():
    def prepare(self):
        self.type = None

    def get_type_from_parameter(self,p):
        """
        get ALU type according paramter name
        paramters:
            p: a paramter
        return:
            None if not find type, else return type
        """
        place_info,encoding = control_LUT.ALUS.get_info(p)
        if place_info is not None:
            return "ALUS"
        place_info,encoding = control_LUT.ALUD.get_info(p)
        if place_info is not None:
            return "ALUD"
        return None

    def scan1(self,dt):
        """
        first dtokens scan, decide alu type
        """
        if dt.value != "ALU":
            return

        for p in dt.parameters:
            self.type = self.get_type_from_parameter(p)
            if self.type is None:
                continue
            return

        raise SyntaxError('unsupport ALU control "{}"'.format(dt))
    
    def scan2(self, dt):
        """
            second scan, if you decide to translate dtoken to another dtoken
            return a not None object(dtoken or dtoken list).
        """
        if dt.value == "ALU":
            r = copy.deepcopy(dt)
            r.value = self.type
            return r
        
        if dt.value == "BUS":
            r = copy.deepcopy(dt)
            for idx,p in enumerate(r.parameters):
                if p == "ALU":
                    r.parameters[idx] = self.type
            return r
        return None
DEFAULT_TRANSLATOR = [alu_translater()]

class hl_dtoken_converter:
    def __init__(self,dtoken_translators = DEFAULT_TRANSLATOR):
        self.dtokens_translater = dtoken_translators


    def convert(self, dtoken_lines):
        """
            generate hardware level dtoken that will convert to machine code
            1. remove jump mark(also add jump mark to jump table)
            2. convert decoder script level mark to  hardware level control mark.
        """
        hl_dtokens = []
        for lineno, one_line in dtoken_lines:
            a = []
            for one_dtoken in one_line:
                for one_translater in self.dtokens_translater:
                    one_translater.scan1(one_dtoken)
            
            for one_dtoken in one_line:
                for one_translater in self.dtokens_translater:
                    r = one_translater.scan2(one_dtoken)
                    if r is None:
                        a.append(one_dtoken)
                    else:
                        a.append(r)
                        break
            
            if len(a) > 0:
                hl_dtokens.append([lineno, a])

        return hl_dtokens