import sys
def print_dec_vec():
    for x in range(256):
        print("# ---- 0x{:0>2X} ---- ".format(x))
        if x == 0:
            SEG_NAME = 'STAGE_CHECK_INTERRUPT'
        elif x & 0xF == 1:
            if (x >> 4) & 1:
                SEG_NAME = 'CSEG_ACALL_ADDR11'
            else:
                SEG_NAME = 'CSEG_AJMP_ADDR11'
        else:
            l = x & 0xF
            h = x & 0xF0
            if l >= 8:
                SEG_NAME = f"IRSEG_{h + 8:X}_{h + 0xF:X}"
            elif l >= 6:
                SEG_NAME = f"IRSEG_{h + 6:X}_{h + 7:X}"
            elif x in (0xE2,0xE3):
                SEG_NAME = f"IRSEG_E2_E3"
            elif x in (0xF2,0xF3):
                SEG_NAME = f"IRSEG_F2_F3"
            else:
                SEG_NAME = f"IRSEG_{x:X}"

        for _ in range(2):
            print(f"J({SEG_NAME})")

print("gen")
with open("decoder_template.ds",mode="w+") as fh:
    sys.stdout = fh
    print_dec_vec()
