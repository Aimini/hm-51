from abc import abstractmethod
from .. import micro_control 


class empty_translator():
    """
    a translator than do nothing, providing create dtoken function.
    """
    @abstractmethod
    def prepare(self):
            pass

    @abstractmethod
    def scan(self, dt):
        """
        you can get info from dtokens in current line.
            dt: dtoken
        """
        pass
    
    @abstractmethod
    def translate(self, dt):
        """
        after scan, you might translate some dtoken to other dtokens.
        If return None, meaing using origin dtoken, else using dtokens that you returned.
            dt: dtoken
                dtoken might be translated.
        """
        pass

    
    def create_jump(self, lineno, type):
        r = micro_control.MicroCTL(lineno, micro_control.PAR_CONTROL, "JUMPABS")
        r.parameters = [type]
        return r

    def create_address(self, lineno, addr):
        r = micro_control.MicroCTL(lineno, micro_control.PAR_CONTROL, "ADDRESS")
        r.parameters = [addr]
        return r

    def create_immed(self, lineno, value):
        r = micro_control.MicroCTL(lineno, micro_control.PAR_CONTROL, "IMMED")
        r.parameters = [value]
        return r

    def create_bus(self, lineno, sel):
        r = micro_control.MicroCTL(lineno, micro_control.PAR_CONTROL, "BUS")
        r.parameters = [sel]
        return r
