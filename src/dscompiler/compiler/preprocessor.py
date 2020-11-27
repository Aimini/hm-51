import os
from io import StringIO
import pathlib
import shlex
from typing import Iterable



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

        
class PreprocessError(Exception):
    def __init__(self, inc_chain_Info:Iterable[LineInfo], diretive, args ,info = ''):
        self.directive = diretive
        self.inc_chain_Info = inc_chain_Info
        self.args = args
        self.info = info

class Preprocessor():
    """
    convert string like  '"s0","a+b","c+d"' to a list like ['s0', 'a+b', 'c+d']
        args_str: str
    """

    def __init__(self, file):
        self.file = pathlib.Path(file)
        self.filedir = self.file.parent
        # the include file chain information of the current line
        #  [LineInfo, LineInfo, ....]
        self._inc_chain_info = []
        # all lines info
        # each element in this list is a include file chain list which
        # have the same meaning as self._inc_chain_info,
        # the lineno start from 1
        # [
        #   [LineInfo, LineInfo] #line 0
        # ]
        self._all_lines_info = [None]
        #final file
        self._outputfile = StringIO()
        # provide information of directive of DEVVEC
        self._decveclineno = None
        self._decvecnum = None
        # how many line we scanned
        self._linecnt = 0

    def decvecinfo(self):
        return self._decveclineno, self._decvecnum

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

    def _preprocess_decvec(self,args):
        self._decveclineno = self._linecnt
        self._decvecnum = int(args[0], 0)

    def _filter_directive_args(self, args):
        ret = []
        previous_split = True
        for one in args:
            if one == ',':
                if previous_split:
                    return PreprocessError(list(self._inc_chain_info), None, ret, "unexpect ','")
                previous_split = True
            else:
                if not previous_split:
                    return PreprocessError(list(self._inc_chain_info), None, ret," directive arguments should split by  ','")
                previous_split = False
                ret.append(one)
        return ret

    def _directive(self, args):
        name = args[1]  # skip '@'
        args = self._filter_directive_args(args[2:])
        if isinstance(args, PreprocessError):
            args.directive = name
            raise args

        if name == "INC":
            self._preprocess_include(args)
        elif name == "DECVEC":
            self._preprocess_decvec(args)
        else:
            raise PreprocessError(list(self._inc_chain_info), name, args, "unknow directive")
        
    def _preprocess_file(self, fileobj):
        for row, s in enumerate(fileobj.readlines()):
            self._linecnt += 1
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

