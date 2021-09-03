import os
import subprocess

chia_directory = '/home/keysys/chia-blockchain/'

# chia_directory = os.getcwd()
venv = chia_directory + 'venv/bin/python'
# os.chdir(chia_directory)
subprocess.check_call((venv + 'chia plotnft show').split(), cwd=chia_directory)
# subprocess.check_call('chia plotnft show'.split(), cwd=chia_directory)
