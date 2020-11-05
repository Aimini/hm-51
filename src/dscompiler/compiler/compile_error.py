class CompileError(Exception):
    def __init__(self, lineno, info) -> None:
        '''
            lineno: int
                line number in the preprocessed file, start from 0
            info:
                the extra info
        '''
        self.lineno = lineno
        self.info = info