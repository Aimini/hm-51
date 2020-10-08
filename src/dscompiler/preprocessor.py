import os
from ast import Str
from io import StringIO
import pathlib
import shlex
from typing import Sequence




class LineInfo:
    def __init__(self):
        self.str = None
        self.row = None
        self.file = None

    def copy(self):
        ret = LineInfo()
        ret.str = self.str
        ret.row = self.row
        ret.file = self.file
        return ret
class Preprocessor():
    """
    convert string like  '"s0","a+b","c+d"' to a list like ['s0', 'a+b', 'c+d']
        args_str: str
    """

    def __init__(self, file):
        self.file = pathlib.Path(file)
        self.filedir = self.file.parent
        self._inc_chain_info = []
        self._all_lines_info = []
        self._outputfile = StringIO()

    def result(self): 
        self._preprocess_include([self.file.name])
        self._outputfile.seek(0)
        return self._outputfile

    def _preprocess_include(self, arg_tokens):
        replacement = arg_tokens[1:]

        incfile = arg_tokens[0]
        incfilepath = str(self.filedir / incfile)

        linfo = LineInfo()
        linfo.file = incfilepath
        self._inc_chain_info.append(linfo)

        with open(incfilepath, "r") as inc_fh:
            content = inc_fh.read()
            # replace include argument string
            for idx, one_arg in enumerate(replacement):
                content = content.replace(f"@{idx}", one_arg)
            if not content.endswith(os.linesep):
                content += os.linesep
            # convert string to lines
            self._preprocess_file(StringIO(content))
        self._inc_chain_info.pop()


    def _filter_directive_args(self, args):
        ret = []
        previous_split = True
        for one in args:
            if one == ',':
                if previous_split:
                    raise Exception("unexpect ',' in directive")
                previous_split = True
            else:
                if not previous_split:
                    raise Exception(" directive arguments should split by  ','")
                previous_split = False
                ret.append(one)
        return ret

    def _directive(self, args):
        name = args[1]  # skip '@'
        args = self._filter_directive_args(args[2:])
        if name == "INC":
            self._preprocess_include(args)
        else:
            raise Exception("unknow directive {!r}".format(name))
        
    def _preprocess_file(self, fileobj):
        for row, s in enumerate(fileobj.readlines()):
            self._inc_chain_info[-1].row = row + 1
            self._inc_chain_info[-1].str = s

            directivestr = s.lstrip()
            if len(directivestr) and directivestr[0] == '@':
                sh = shlex.shlex(directivestr, posix=True, punctuation_chars=True)
                self._directive(list(sh))
            else:
                info =[_.copy() for _ in self._inc_chain_info]
                self._all_lines_info.append(info)
                self._outputfile.write(s)
                
                
        
        #self._outputfile.write('\n')
        #self._all_lines_info.append(list(self._inc_chain_info))

    def getlineinfo(self, lineno):
        '''
        lineno:
            line no in preprocessed file, you will
            get the line's information in the raw
            file
        ret: (filename, row number)

        '''
        return self._all_lines_info[lineno]

