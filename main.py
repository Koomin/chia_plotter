import os
import subprocess

chia_directory = '/home/keysys/chia-blockchain/'
print(os.getcwd())
#os.chdir(chia_directory)
subprocess.check_call('. ./activate'.split(), cwd=chia_directory)
subprocess.check_call('chia plotnft show'.split(), cwd=chia_directory)