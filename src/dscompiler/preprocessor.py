
from ast import Str
from io import StringIO
import pathlib
import shlex
from typing import Sequence


class Token:
    def __init__(self, s: str, column):
        self.str = s
        self.column = column


class LineInfo:
    def __init__(self, s: str, tokens, file, row):
        self.s = s
        self.tokens: list = tokens
        self.file = file
        self.row = row


class Preprocessor():
    """
    convert string like  '"s0","a+b","c+d"' to a list like ['s0', 'a+b', 'c+d']
        args_str: str
    """

    def __init__(self, file):
        self.file = pathlib.Path(file)
        self.filedir = self.file.parent
        self.outputfile = StringIO()

    def result(self):
        with open(self.file) as inc_fh:
             self._preprocess_file(inc_fh)
        self.outputfile.seek(0)
        return self.outputfile

    def _preprocess_include(self, arg_tokens):
        incfile = arg_tokens[0]
        incfilepath = str(self.filedir / incfile)
        replacement = arg_tokens[1:]
        
        with open(incfilepath, "r") as inc_fh:
            content = inc_fh.read()
            # replace include argument string
            for idx, one_arg in enumerate(replacement):
                content = content.replace(f"@{idx}", one_arg)
            # convert string to lines
            self._preprocess_file(StringIO(content))
            self.outputfile.write('\n')

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
        for s in fileobj.readlines():
            directivestr = s.lstrip()
            if len(directivestr) and directivestr[0] == '@':
                sh = shlex.shlex(directivestr, posix=True, punctuation_chars=True)
                self._directive(list(sh))
            else:
                self.outputfile.write(s)
