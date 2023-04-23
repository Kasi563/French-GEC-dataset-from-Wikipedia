"""
This is a script used to create a new dataset, based on the extracted dataset, that has no correction in it. In other words, there is no difference between the X column and the y column. The generation of the dataset with minimal errors in the text is possible thanks to the preprocess_y function.
"""
import polars as pl
from main import clean_column
import logging
import os
import random
from get_file_names import get_file_names
from tqdm import tqdm



def preprocess_y(data: pl.DataFrame):
    """
    Preprocesses the y column from wikipedia extraction. Requirements: must combine all the files from individual workers from extraction to have a continuous number of titles that doesn't overlap.
    Columns X and y must be "en amont" cleaned in exactly the same way.
    """
    X = []
    Y = []
    series = []
    current_title = ""
    rY = []
    c = 0

    for row in data:
        series.append(row)

    for i in range(len(series[0])):
        x = series[0][i]
        y = series[1][i]
        title = series[3][i]
        if title != current_title:
            current_title = title
            trY = _correct(X, Y)
            for f in range(len(trY)):
                rY.append(trY[f])
            if i != len(rY):
                pass
            c += i
            X = []
            Y = []

        X.append(x)
        Y.append(y)

    trY = _correct(X, Y)
    for f in range(len(trY)):
        rY.append(trY[f])

    Y = []
    for y in rY:
        if not y in Y:
            Y.append(y)
    return Y


def _correct(X, y):
    """
    Takes two arrays corrects the y sentence of multiple X,y pairs featuring the same sentence but different y values (corrections).
    Belongs to preprocess_y function
    """
    length = len(X)
    for i in range(length - 1, -1, -1):
        standard = y[i] # reverse indexing
        standard_x = X[i]
        second = standard

        for g in range(length -1, -1, -1):
            if y[g] == standard_x and g != i:
                y[g] = standard
                second = X[g]
            elif y[g] == second:
                y[g] = standard
                second = X[g]
    return y


def create_from_extraction_data(file_path: str, clean_data=False) -> pl.DataFrame:
    """
    Given a .csv file (`file_path`) with X, y pairs from a Wikipedia extraction, and with the following structure:
        - `Thies is th ancient correction` --> `This is th ancient correction`
        - `This is th ancient correction` --> `This is the ancient correction`
    
    It produces the X,y pair: `Thies is th ancient correction` --> `This is the ancient correction`
    It also works with infinite "corrections" made to the sentence.
    """
    if not os.path.exists(file_path):
        logging.warning("File %s doesnt exist", file_path)
        return None
    
    data = pl.read_csv(file_path)
    Ys = pl.Series(preprocess_y(data))
    if clean_data:
        Ys = clean_column(Ys)
    Ys = Ys.drop_nulls()

    result = []
    for y in Ys:
        result.append(y)

    return pl.DataFrame([result, result], schema=["X", "y"])


if __name__ == '__main__':
    # Source path is a directory containing subdirectories which contains the actual .csv files from a wikipedia extraction.
    source = r"D:\data\French corpora collection\Wikipedia Extraction Files"
    result_path = r"D:\data\French corpora collection\Wikipedia Preprocessed Files2"
    # Maximum length of collected sentences.
    MAX_SENTS = 4_900_000

    files_to_extract = get_file_names(source, extension=".csv")
    
    random.shuffle(files_to_extract)

    file_index = 0
    total_len = 0

    for file in tqdm(files_to_extract):
        data = create_from_extraction_data(file)
        total_len += len(data)
        if total_len > MAX_SENTS:
            print("Exiting extraction")
            break
        data.write_csv(os.path.join(result_path, f"plain_{file_index}.csv"))
        file_index += 1
        print(f"Total length: {total_len}")
    
    print(f"Total length: {total_len}")
    print(file_index)