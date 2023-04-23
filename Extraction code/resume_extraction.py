import pandas as pd
import logging
import os


def _load_data(directory_path: str) -> list[pd.DataFrame]:
    """
    Function takes a directory path and returns a list of pandas DataFrame objects from the csv files in the directory.
    """
    # Cheks if the direcory exists
    if not os.path.isdir(directory_path):
        raise ValueError("Path to directory does not exist: " +  directory_path)
    
    files_path = os.listdir(directory_path)
    data = []
    for file in files_path:
        if file.endswith(".csv"):
            data.append(pd.read_csv(directory_path + "\\" + file))
    return data


def _get_titles(data: list[pd.DataFrame]) -> list[str]:
    """
    Takes a list of pandas DataFrames, and gets all the different titles in the titles column.
    """
    titles = []

    for file in data:
        for title in file["title"]:
            if not title in titles:
                titles.append(title)

    return titles


def get_extracted_titles(path: str) -> list[str]:
    """
    Given a path to a directory with csv files from an extraction, the function gets all the titles of the Wikipedia pages extracted in order for the program to resume where it left off. Returns a list of all the Wikipedia titles present in the directory's csv files in the column 'titles'.
    """
    if not path == None:
        data = _load_data(path)
        print("Done loading title data")
        titles = _get_titles(data)
        logging.info(f"Number of titles extracted from directory {path} is {len(titles)}")
        return titles
    return []

