import sys
def print_2div(start, end):
    m = int((start + end)/2)
    if m + 1 < end:
	    print(f"RF(IR), BLT(0x{m:X},IRSEG_{start:X}_{m - 1:X})")
	    print(f";; IRSEG_{m:X}_{end - 1:X}")
	    print_2div(m, end)
    elif m + 1 == end:
        print(f"RF(IR), BLT(0x{m:X},IRSEG_{m - 1 :X})")
        print(f"IRSEG_{end - 1:X}: ;--------------------")
        print("")
        print(";------------------------------")
        print("")
        print("")

    if start + 1 < m:
	    print(f"IRSEG_{start:X}_{m - 1:X}:")
	    print_2div(start,m)
    else:
        print(f"IRSEG_{start:X}: ---------------------")
        print("")
        print(";------------------------------")
        print("")
        print("")
        
print("gen")
sys.stdout = open("decoder_template.ds",mode="w+")
print_2div(0, 0x100)
sys.stdout.close()