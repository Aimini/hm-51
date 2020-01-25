from __asmconst import SFR_A, SFR_PSW


class SIMRAM():
    def __init__(self):
        self.RAM = [0 for _ in range(0x100)]

    def __getitem__(self, k: int):
        return self.RAM[k]

    def __setitem__(self, k: int, v):
        if k == SFR_PSW.x:
            pf = self.RAM[SFR_PSW.x] & 1
            self.RAM[SFR_PSW.x] = (v & 0xFE) | pf
        else:
            self.RAM[k] = v
            
        if k == SFR_A.x:
            pf = bin(self.RAM[SFR_A.x]).count('1') & 1
            self.RAM[SFR_PSW.x] &= 0xFE
            self.RAM[SFR_PSW.x] |= pf

    def bit(self, addr, idx):
        return (self[addr] >> idx) & 1

    def set_bit(self, addr, idx, value):
        mask = ~(1 << idx)
        self[addr] = (self[addr] & mask) | (value << idx)
        