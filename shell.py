import colonscript5
from sys import argv
with open(argv[1],"r") as f:
    runtime = colonscript5.ColonScript5(f.readlines())
    runtime.create_functions()
    runtime.interpret_lines()