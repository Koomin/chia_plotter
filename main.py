import subprocess
import json
import logging
import sys
import shutil
import uuid
import concurrent.futures
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


def run_plotting(k, directories):
    thread_id = uuid.uuid4()
    start = time.time()
    logging.info(f'Starting plotter with ID {thread_id}.')
    directory_path = enough_free_space(k, directories)
    cmd = f'chia plots create -k {k} -t {temp_path} -d {directory_path} -c {plotting_address}'
    try:
        subprocess.check_call(cmd.split(), cwd=chia_directory)
    except IOError:
        logging.error('Chia directory wrong provided.')
        sys.exit()
    end = time.time()
    execution_time = timedelta(seconds=end - start)
    logging.info(f'Exit plotter with ID {thread_id} - execution time {execution_time}.')


def check_disk_space(directories_list):
    for directory in directories_list:
        try:
            total, used, free = shutil.disk_usage(directory)
            free = free // (2 ** 30)
            DISKS_FREE_SPACE[directory] = free
        except FileNotFoundError:
            logging.error(f'Cannot find directory : {directory}')
            continue


def enough_free_space(k, directories):
    for path in directories:
        if DISKS_FREE_SPACE.get(path) and PLOT_SIZE[k] * 1.05 < DISKS_FREE_SPACE.get(path):
            DISKS_FREE_SPACE[path] = DISKS_FREE_SPACE[path] - PLOT_SIZE[k]
            return path
    logging.error('Not enough disk space - interrupting.')
    sys.exit()


if __name__ == "__main__":
    while True:
        check_disk_space(final_directories)
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            executor.map(run_plotting(k_size, final_directories), range(threads))
