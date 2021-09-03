import os
import subprocess

chia_directory = '/home/keysys/chia-blockchain/'
print(os.getcwd())
#os.chdir(chia_directory)
subprocess.check_call('. ./activate', cwd=chia_directory)
subprocess.check_call('chia plotnft show', cwd=chia_directory)