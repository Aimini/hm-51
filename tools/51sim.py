import sys
import pathlib
import js2py

jsfilename = [
     "51vm_core.js",
     # "51vm_operand.js",
     # "51vm_operation.js",
     # "51vm_opcode_decoder.js",
    # "51vm_ctl.js",
    # "51vm_peripheral.js",
    # "py_my_debug.js",
]

jsdir = pathlib.Path(sys.argv[0]).parent / "51js"
jsdir  /= "src"
jstext = ""
for one in jsfilename:
    fh = open(jsdir / one)
    jstext += fh.read()
    jstext += '\n'


context = js2py.EvalJs()
context.execute(jstext)
# print(context.vm.IRAM)

