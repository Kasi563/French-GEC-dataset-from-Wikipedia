"""
Is doing the exact same thing as main.py, except that it uses multiprocessing to accelerate the process.
"""
import logging
import os
import time
import multiprocessing
from main import clean_folder, get_global_stats

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')

start = time.time()
CORRUPTION_PROBA = 0.0012


if __name__ == "__main__":
    # Paths:
    source = r"D:\data\French corpora collection\WIKIPEDIA complete\Wikipedia Extraction Files"
    result_path = r"D:\data\French corpora collection\WIKIPEDIA complete\Wikipedia Preprocessed Files2"
    num_workers = 6

    if num_workers > multiprocessing.cpu_count():
        raise ValueError("CPU does not support more than {num_workers} parallel processes because of hardware limitations. ")

    folders = []
    folders_path = []
    for folder in os.listdir(source):
        folder_path = os.path.join(source, folder)
        folders_path.append(folder_path)
        folders.append(folder)

    pool = multiprocessing.Pool()
    r = pool.starmap(clean_folder, [(folders_path[i], folders[i], result_path) for i in range(len(folders))])
    
    get_global_stats(result_path)

    logging.info("Exec time: " + str(time.time() - start))