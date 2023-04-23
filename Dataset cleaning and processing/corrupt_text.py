import polars as pl
from corruptor import create_corrupter
import os
import multiprocessing

CORRUPTION_PROBA = 0.0012


def get_file_names(source: str, extension=".csv") -> list[str]:
    """
    Given a source path to a directory, this function extracts every file ending with the extension in every subdirectory and returns a list of complete file paths.
    """
    result = []
    folders = os.listdir(source)
    for folder in folders:
        folder_path = os.path.join(source, folder)
        for file in os.listdir(folder_path):
            if file.endswith(extension):
                file_path = os.path.join(folder_path, file)
                result.append(file_path)
    
    return result


corrupter = create_corrupter(None, "corruptor_main.pkl")
def corrupt(text: str, probability=CORRUPTION_PROBA):
    return corrupter.corrupt(text, probability=probability)


def corrupt_file(file_path):
    """
    Given a path to a csv fiole, corrupts the file 
    """
    if not file_path.endswith('.csv'):
        raise ValueError(f"The file with the path {file_path} does not exist")
    data = pl.read_csv(file_path)
    data = data.with_columns(data["X"].apply(corrupt))
    data.write_csv(file_path)
    print(f"Done with file {file_path}")


if __name__ == "__main__":
    root = r"D:\data\French corpora collection\WIKIPEDIA\Wikipedia Preprocessed Files main reduced corrupted"
    num_workers = 7

    if num_workers > multiprocessing.cpu_count():
        raise ValueError("CPU does not support {num_workers} parallel processes because of hardware limitations. ")

    files = get_file_names(root)
    print(files)
    print(len(files))
    pool = multiprocessing.Pool(num_workers)
    pool.map(corrupt_file, files)
