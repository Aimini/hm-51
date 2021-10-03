#
# Author AI
# splite binary file with N bytes per address 
# to indivaul binary files that consist with one byte per address 


import sys
import pathlib
usage = """
 splitbytebin.py <input_file> <n>
    Treat input_file as a file containing <n> bytes per line,
    the <n>th bytes in each line are stored in a separate file. 
    The output file name is the original file name followed by <n>.

    inpu_file:
        input file name
    n: int
        how many byte per line

    for example

        input.txt
            ABCDEF

        spiltbytebin.py input.txt 3

        input.txt1
            AD
        input.txt2
            BE    
        input.txt3
            CF
"""

if len(sys.argv) < 3:
    print(usage)
else:
    infile = pathlib.Path(sys.argv[1])
    n = int(sys.argv[2])
    with open(infile,'rb') as fih:
        data = fih.read()
        sdata = [data[x:x+n] for x in range(0,len(data),n)]
        zdata = zip(*sdata) 
        for i,od in enumerate(zdata):
            
            with open( infile.parent /(infile.stem + str(i) + infile.suffix),'wb') as foh:
                foh.write(bytearray(od))
