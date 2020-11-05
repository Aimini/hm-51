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
import copy
import random
import string

from .empty_translator import TranlatorError
from .. import micro_control
from .alu_translator import ALUTranslator
from .jump_translator import JumpTranslator
from .load_immed_translator import LoadImmedTranslator
from ..CTL_LUT.control_LUT import JUMPABS
from ..CTL_LUT import ALULUTtools
from ..compile_error import CompileError

DEFAULT_TRANSLATOR = (ALUTranslator(), 
                      JumpTranslator(), LoadImmedTranslator())





class MicroControlConverter:
    def __init__(self,vec_lineno = None,vec_num = None, dtoken_translators=DEFAULT_TRANSLATOR):
        self.vec_lineno = vec_lineno
        self._vec_num = vec_num
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
        self.hl_microinstructions = []
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
                    self.hl_microinstructions.append([lineno, a])

            except TranlatorError as e:
                e.lineno = lineno
                raise e
        return self.hl_microinstructions


class DecvecConverter:
    def __init__(self,hl_microinstructions,vec_lineno = None,vec_num = None):
        self.vec_lineno = vec_lineno
        self._vec_num = vec_num
        self.hl_microinstructions = hl_microinstructions
        #record what will replace the VEC
        # {
        #   VECindex0 : { token0, token1}，
        #   VECindex1 : { token0, token1}
        #   ...
        # }
        self.replacelines = {} 

        #record the jump marks that will be inserted into the target that in the VEC parameter.
        # {
        #   VECindex0 : { token0, token1}，
        #   VECindex1 : { token0, token1}
        #   ...
        # }
        self.insertlines = {}

    def _is_only_vec_ctl(self, microinstrction):
        if len(microinstrction) == 0:
            return False

        for ctl in microinstrction:
            if ctl.value != "VEC":
                return False
        return True

    def _is_any_ctl(self, microinstrction):
        if len(microinstrction) == 0:
            return False

        for ctl in microinstrction:
            if ctl.type != micro_control.JUMP_MARK:
                return True
        return False

    def _find_any_jump(self, microinstrction):
        if len(microinstrction) == 0:
            return None

        for ctl in microinstrction:
            if ctl.type == micro_control.CONTROL:
                if JUMPABS.have_encoding_name(ctl.name):
                    return ctl.name
        return None

    def _generate_vec_jump(self, insert_microinstruction, insertjumplabels):
        for i, (lineno, microinstruction) in enumerate(insert_microinstruction):
            no_jump = True
            for ctl in microinstruction:
                if ctl.type == micro_control.PAR_CONTROL and ctl.value == 'JUMPABS':
                    no_jump = False

                    jtype = ctl.parameters[0]
                    if  ALULUTtools.is_uncondition(jtype): # no condtion jump, so copy itdirectly 
                        return True
                    elif ALULUTtools.is_condtion(jtype):
                        # condition jump? we can't predict where it's going on
                        # so keep the code, try next microinstruction
                        break


            if no_jump: # no jump, so we create jump
                r0 = micro_control.MicroCTL(lineno, micro_control.PAR_CONTROL, "JUMPABS")
                r0.parameters = ["J"]
                r1 = micro_control.MicroCTL(lineno, micro_control.PAR_CONTROL, "ADDRESS")
                r1.parameters = [insertjumplabels[i]]
                #append a jump
                microinstruction.extend([r0, r1])
                return True
        
        return False

    def _generate_vec_insert(self, target_label ,current_index,target_index ):
        current_lineno = self.hl_microinstructions[current_index][0]
        i = target_index
        insert_microinstructions = []
        while i < len(self.hl_microinstructions) and len(insert_microinstructions) < 2:
            if self._is_any_ctl(self.hl_microinstructions[i][1]):# skip line only have empty/jump mark
                cp = copy.deepcopy(self.hl_microinstructions[i])
                cp[0] = current_lineno
                insert_microinstructions.append(cp)
            i += 1

        # create target jump label  
        jumplabel =''.join(random.choices(string.ascii_uppercase, k=10))
        jumplabel +'_' + target_label
        # record label name(string) we insert
        insertjumplabels = [] 
        for x in range(2):
            labelinsertindex = target_index + 2 + x
            lineno = self.hl_microinstructions[labelinsertindex][0]
            if self.insertlines.get(labelinsertindex) == None:
                insertjumplabels.append(target_label+ '_'+ jumplabel  +  str(x) + '__' )
                r = micro_control.MicroCTL(lineno, micro_control.JUMP_MARK, insertjumplabels[x])
                self.insertlines[labelinsertindex] = [lineno, [r]]
            else:
                insertlabel = self.insertlines.get(labelinsertindex)[1]# already have name cause by another VEC directiver
                insertjumplabels.append(insertlabel[0].value)

            
        if not self._generate_vec_jump(insert_microinstructions, insertjumplabels):
            r0 = micro_control.MicroCTL(current_lineno, micro_control.PAR_CONTROL, "JUMPABS")
            r0.parameters = ["J"]
            r1 = micro_control.MicroCTL(current_lineno, micro_control.PAR_CONTROL, "ADDRESS")
            r1.parameters = [target_label]
            insert_microinstructions[0] = [current_lineno, [r0, r1]]
        self.replacelines[current_index] =  insert_microinstructions




    def _find_jump_label(self, label_name):
        '''
        find the hl_microinstructions[index] that cantain label_name
        return:
            return the index if find otherwise is return -1
        '''
        for i, (lineno, mcrioinstruction) in enumerate(self.hl_microinstructions):
            for ctl in mcrioinstruction:
                if ctl.type == micro_control.JUMP_MARK and ctl.value == label_name:
                    return i
        return -1

    def result(self):
        if self.vec_lineno == None:
            return self.hl_microinstructions

        # find vec start index
        vecstartindex = 0
        for  i, (lineno, microinstruction) in enumerate(self.hl_microinstructions):
            if lineno >= self.vec_lineno:
                vecstartindex = i
                break
        
        # find the index of the target jump label in hl_microinstrcutions
        for n in range(self._vec_num):
            idx  = vecstartindex + n
            if idx >= len(self.hl_microinstructions):
                raise CompileError(self.vec_lineno, "not enough 'VEC' for this diretive")
            lineno, microinstruction = self.hl_microinstructions[idx]
            if not self._is_only_vec_ctl(microinstruction):
                raise CompileError(lineno, "the micro-control follow @DECVEC directive must be 'VEC'")
            microctl = microinstruction[0]
            target_label = microctl.parameters[0]
            target_index = self._find_jump_label(target_label)
            # where is my label?
            if target_index == -1:
                raise CompileError(lineno, "'VEC' paramater label {!r} not exists".format(target_label))
            self._generate_vec_insert(target_label, idx, target_index)
        
        # produce the final microinstrcution stream
        ret = []
        for i, info in  enumerate(self.hl_microinstructions):
            if self.replacelines.get(i) != None:
                for ins in self.replacelines.get(i):
                    for s in ins[1]:
                        assert(not isinstance(s, list))
                    ret.append(ins)
            elif self.insertlines.get(i) != None:
                a= self.insertlines.get(i)
                for s in a[1]:
                    assert(not isinstance(s, list))
                ret.append(a)
                ret.append(info)
            else:
                ret.append(info)
        return ret