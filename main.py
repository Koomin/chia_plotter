import subprocess
import json
import logging
import sys
import threading

try:
    with open('config.json') as config:
        config_data = json.load(config)
        chia_directory = config_data['chia_directory']
        k_size = config_data['k_size']
        temp_path = config_data['temp_path']
        directory_path = config_data['directory_path']
        plotting_address = config_data['plotting_address']
        threads = int(config_data["threads"])
        logging.info('Config loaded correctly.')
except IOError as e:
    logging.error(f'Cannot find config file.')
    sys.exit()
except ValueError:
    logging.error(f'Wrong number of threads provided.')
    sys.exit()
except KeyError:
    logging.error(f'You didn\'t provide all config data.')
command = f'chia plots create -k {k_size} -t {temp_path} -d {directory_path} -c {plotting_address}'


class PlottingThread(threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID

    def run(self):
        logging.info(f'Starting {self.threadID} plotter.')
        run_plotting(command)
        logging.info(f'Exit {self.threadID} plotter.')


def run_plotting(cmd):
    try:
        subprocess.check_call(cmd.split(), cwd=chia_directory)
    except IOError:
        logging.error('Chia directory wrong provided.')
        sys.exit()


while True:
    for idx in range(0, threads):
        PlottingThread(idx).start()
    while threading.activeCount() > 0:
        logging.info(f'{threading.activeCount()} plotters run.')
