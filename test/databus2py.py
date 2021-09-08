import sys
import base64
import lzma
def convert(dbfile, pyfile):
    s = ""
    with open(dbfile,"rb") as dbfile:
        with open(pyfile, "w") as pyfile:
            s = dbfile.read()
            res = base64.b64encode(lzma.compress(s))
            pyfile.write('DATA = ')
            pyfile.write(repr(res))

if __name__ == "__main__":
    usage = """
    convert data bus file(binary format) to a python file that contain a string,
    the string is the byte-array representation of the data bus.
    usage:
        databus2py 
        input_file:
            data bus file
        output_file:
            python file
    """
    
    if len(sys.argv) < 3:
        print(usage)
    else:
        convert(sys.argv[1], sys.argv[2])