import subprocess
import json
import logging
import sys
import shutil
import threading
import time
from datetime import timedelta

PLOT_SIZE = {
    "25": 0.6,
    "32": 101.4,
    "33": 208.8,
    "34": 429.8,
    "35": 884.1
}

DISKS_FREE_SPACE = {

}

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

try:
    with open('config.json') as config:
        config_data = json.load(config)
        chia_directory = config_data['chia_directory']
        k_size = config_data['k_size']
        temp_path = config_data['temp_directory']
        final_directories = config_data['list_of_final_directories']
        plotting_address = config_data['plotting_address']
        threads = int(config_data["threads"])
        logging.info('Config loaded correctly.')
except IOError as e:
    logging.error(f'Cannot find config file - interrupting.')
    sys.exit()
except ValueError:
    logging.error(f'Wrong number of threads provided - interrupting.')
    sys.exit()
except KeyError:
    logging.error(f'You didn\'t provide all config data - interrupting.')
    sys.exit()


class PlottingThread(threading.Thread):
    def __init__(self, threadID, k, directories):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.k = k
        self.directories = directories

    def run(self):
        logging.info(f'Starting {self.threadID} plotter.')
        start = time.time()
        run_plotting(self.k, self.directories)
        end = time.time()
        execution_time = timedelta(seconds=end - start)
        logging.info(f'Exit {self.threadID} plotter - execution time {execution_time}..')


def run_plotting(k, directories):
    directory_path = enough_free_space(k, directories)
    if directory_path:
        cmd = f'chia plots create -k {k} -t {temp_path} -d {directory_path} -c {plotting_address}'
        try:
            subprocess.check_call(cmd.split(), cwd=chia_directory)
        except IOError:
            logging.error('Chia directory wrong provided.')
            sys.exit()


def check_disk_space(directories_list):
    for directory in directories_list:
        try:
            total, used, free = shutil.disk_usage(directory)
            free = free // (2 ** 30)
            DISKS_FREE_SPACE[directory] = free
            logging.info(f'Free space {directory} : {DISKS_FREE_SPACE[directory]}')
        except FileNotFoundError:
            logging.error(f'Cannot find directory : {directory}')
            continue


def enough_free_space(k, directories):
    for path in directories:
        if DISKS_FREE_SPACE.get(path) and PLOT_SIZE[k] * 1.05 < DISKS_FREE_SPACE.get(path):
            DISKS_FREE_SPACE[path] = DISKS_FREE_SPACE[path] - PLOT_SIZE[k]
            return path
    logging.error('Not enough disk space - interrupting.')
    return False


if __name__ == "__main__":
    threads_list = []
    while True:
        go_on = False
        if len(threads_list) < threads:
            check_disk_space(final_directories)
            for thread in range(threads):
                running_thread = PlottingThread(thread, k_size, final_directories)
                threads_list.append(running_thread)
                running_thread.start()
        while not go_on:
            if threads_list:
                status_list = [t.is_alive() for t in threads_list]
                if True not in status_list:
                    go_on = True
                    threads_list = []
            else:
                go_on = False
