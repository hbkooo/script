# in one .py file to call other .py file

import subprocess

cmd = "python png2jpg.py "
print(cmd)
process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
output = process.communicate()[0]
print(output)
