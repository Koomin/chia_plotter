import os
import subprocess

chia_directory = '/home/keysys/chia-blockchain/'

# chia_directory = os.getcwd()
venv = chia_directory + 'venv/bin/python chia plotnft show'
# os.chdir(chia_directory)
subprocess.check_call('chia plotnft show'.split(), cwd=chia_directory)
# subprocess.check_call('chia plotnft show'.split(), cwd=chia_directory)
