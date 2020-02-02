from __asmconst import SFR_A, SFR_PSW


class SIMRAM():
    def __init__(self):
        self.IRAM = [0 for _ in range(0x100)]
        self.SFRAM = [0 for _ in range(0x100)]

    def get_direct(self, addr:int):
        if addr < 0x80:
            return self.IRAM[addr]
        else:
            return self.SFRAM[addr]

    def set_direct(self, addr:int, value:int):
        value &= 0xFF
        if addr < 0x80:
            self.IRAM[addr] = value
        else:
            self.SFRAM[addr] = value
                
            if addr in (SFR_A.x, SFR_PSW.x):
                pf = bin(self.SFRAM[SFR_A.x]).count('1') & 1
                self.SFRAM[SFR_PSW.x] &= 0xFE
                self.SFRAM[SFR_PSW.x] |= pf

    def get_iram(self, addr:int):
        return self.IRAM[addr]
    
    def set_iram(self, addr:int, value:int):
        value &= 0xFF
        self.IRAM[addr] = value

    def get_bit(self, addr:int , idx:int):
        value = self.get_direct(addr)
        return (value >> idx) & 1
        
    def set_bit(self, addr:int, idx:int, value:int):
        mask = ~(1 << idx)
        raw = self.get_direct(addr)
        target = (raw & mask) | ((value&1) << idx)
        self.set_direct(addr, target)


    def bulid_indirect(self, ri_addr:int , indirect_addr:int, value:int):
        self.set_iram(indirect_addr, value)    
        self.set_iram(ri_addr, indirect_addr)
    
    def get_indirect(self, ri_addr:int):
        return self.get_iram(self.get_iram(ri_addr))
    