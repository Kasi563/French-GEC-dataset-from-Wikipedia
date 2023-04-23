import polars as pl
import logging
import os
import clean_template as ct
import re
import time
from tqdm import tqdm
from get_file_names import get_file_names

# Statistiques
nb_sent = 0
nb_cleaned_sent = 0
equal_pairs = 0
nb_of_removed_pipes = 0
curly_braces_removal_rate = 0
bracket_removal_rate = 0
quotation_removal_count = 0
parenthesis_removal_rate = 0
remove_file_tags = 0
ending_with_cap_removal_rate = 0


logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')

start = time.time()


url_pattern = re.compile(r"https?:\/\/\S+.+?")
def remove_urls(x):
    if not isinstance(x, str):
        return x
    return re.sub(url_pattern, "", x)


def remove_brackets(x: str, is_X=False):
    """
    Takes a string and removes all brackets from the string. Returns the string except for when the opening and closing brackets don't match.
    """
    global bracket_removal_rate
    if not isinstance(x, str):
        return x
    brackets_depth = 0
    result = ""
    for char in x:
        if char == "[":
            brackets_depth += 1
        elif char == "]":
            brackets_depth -= 1
        else:
            result += char
    if brackets_depth != 0 and not is_X:
        bracket_removal_rate += 1
        return None
    else:
        return result


def remove_curly_braces(x: str, is_X=False):
    global curly_braces_removal_rate
    """
    Takes a string and removes all brackets from the string. Returns the string except for when the opening and closing brackets don't match.
    """
    if not isinstance(x, str):
        return x
    brackets_depth = 0
    result = ""
    for char in x:
        if char == r"{":
            brackets_depth += 1
        elif char == "}":
            brackets_depth -= 1
        else:
            result += char
    if brackets_depth != 0 and not is_X:
        curly_braces_removal_rate += 1
        return None
    else:
        return result


def delete_unequal_parenthesies(x: str):
    global parenthesis_removal_rate
    """
    Takes a string and removes all parenthesies from the string. Returns the string except for when the opening and closing parenthesies don't match.
    """
    brackets_depth = 0
    if not isinstance(x, str):
        return x
    for char in x:
        if char == r"(":
            brackets_depth += 1
        elif char == r")":
            brackets_depth -= 1
    if brackets_depth != 0:
        parenthesis_removal_rate += 1
        return None
    else:
        return x


def eq_pairs(data: pl.DataFrame):
    """
    Removes the sentences (X) that have the same correction.
    """
    r = 0
    for i in range(len(data["X"])):
        if data["X"][i] == data["y"][i]:
            r += 1
    return data.drop_nulls()


def remove_ending_w_cap(x: str):
    """
    Removes the X,y pairs if y ends with capitalization before periods
    """
    global ending_with_cap_removal_rate
    if isinstance(x, str):
        try:
            char = x[-2]
        except IndexError:
            return x
        if char.isupper():
            ending_with_cap_removal_rate += 1
            return None
    return x


def fix_quotation(x: str, is_X=False):
    global quotation_removal_count
    if not isinstance(x, str):
        return x
    quot_count = 0
    guillemets_count = 0
    for char in x:
        if char == "«":
            quot_count += 1
        elif char == "»":
            quot_count -= 1
        elif char == "\"":
            if guillemets_count >= 0:
                guillemets_count += 1
            else:
                guillemets_count -= 1
    
    if quot_count == 0 and guillemets_count == 0:
        return x
    elif quot_count == 1:
        return x + " »."
    elif quot_count == -1 and not is_X:
        quotation_removal_count += 1
        return None
    elif quot_count > 1 or quot_count < -1 and not is_X:
        quotation_removal_count += 1
        return None
    elif guillemets_count != 0 and not is_X:
        quotation_removal_count += 1
        return None
    else:
        return x


parenthesis_pattern = re.compile(r"\([,?.;\/:!§%*µ£$¤^¨+=})°\]@^_\\`|\-(['{\"#~<>\s]*?\)")
def remove_empty_parenthesies(x: str):
    if not isinstance(x, str):
        return x
    return re.sub(parenthesis_pattern, "", x)


def remove_image_tags(x: str):
    """
    Removes specifically the ugly image tags and only gets the title like this: Image: 'title'.
    """
    global remove_file_tags
    if not isinstance(x, str) or not x:
        return x
    match = re.match(r"(([Ii]mage)|([Ff]ichier)) ?:.+?\.[A-Za-z]{2,4}(.*?\|)*", x)
    if match:
        h, i = match.span()
        if h == 0:
            if not "=" in x[i:]:
                if not x[-1] == ".":
                    return x[i:] + "."
                return x[i:]
            else:
                remove_file_tags += 1
                return None
        remove_file_tags += 1
        return None
    return x


pipe_pattern = re.compile(r"\|")
def remove_pipes(x: str):
    global nb_of_removed_pipes
    """
    Deletes parameter x if there is a pipe char in the string.
    """
    if not isinstance(x, str):
        return x
    search = re.findall(pipe_pattern, x)
    if search:
        nb_of_removed_pipes += 1
        return None
    return x


# An quick way to fix a little problem from the clean_template.py file. 
siècles_quick_fix = re.compile("(?<=[IVXL])\|e(?=e)")
def quick_fix_siècles(x: str):
    if not isinstance(x, str):
        return x
    return re.sub(siècles_quick_fix, "", x)


def clean_column(column: pl.Series, is_X=False, clean_templates=True, probability=0.0012):
    global total_percents
    new_column = []
    for element in column:
        element = ct.remove_templates(element)
        new_el = fix_quotation(remove_brackets(remove_curly_braces(remove_urls(element), is_X), is_X), is_X)
        new_el = quick_fix_siècles(remove_image_tags(remove_empty_parenthesies(new_el)))
        if not is_X:
            new_el = remove_pipes(remove_ending_w_cap(delete_unequal_parenthesies(new_el)))
        new_column.append(new_el)

    return pl.Series(new_column)


def clean_file(file_path: str, clean_templates=True, probability=0.0012) -> pl.DataFrame:
    """
    Takes one file from the extraction and cleans it up.
    """
    if not os.path.exists(file_path):
        logging.warning("File %s doesnt exist", file_path)
        return None
    
    global nb_sent
    global nb_cleaned_sent
    data = pl.read_csv(file_path)

    # Make sure data is not empty
    if data.is_empty():
        return data

    nb_sent += len(data)

    # Clean columns X and y (they need different depths of cleanups).
    new_X = clean_column(data["X"], is_X=True, clean_templates=clean_templates, probability=probability)
    data.replace("X", new_X)

    new_y = clean_column(data["y"], clean_templates=clean_templates, probability=probability)
    data.replace("y", new_y)

    data = data.filter((pl.col("X") != None) & (pl.col("y") != None))

    nb_cleaned_sent += len(data)

    return data


def clean_folder(path: str, dir_name: str, result_path: str):
    assert isinstance(path, str)
    assert isinstance(dir_name, str)
    try:
        files = os.listdir(path)
    except OSError:
        logging.error("Could not find files in directory '%s'", path)
        return False
    start_time = time.time()
    
    save_path = os.path.join(result_path, dir_name)
    try:
        os.mkdir(save_path)
    except FileExistsError:
        logging.warning(f"Saving the cleaned dataset in an already existing directory ({save_path}). Be shure this does not overwrite existing files.")
    
    c = 0
    result = pl.DataFrame()
    for i in tqdm(range(len(files)), f"Cleaning folder {dir_name}..."):
        if ".csv" == files[i][-4:]:
            data = clean_file(os.path.join(path, files[i]), clean_templates=True)
            if not data.is_empty():
                result = pl.concat([result, data])
                if result.estimated_size("mb") >= 20:
                    result.write_csv(os.path.join(save_path, str(c)) + ".csv")
                    result = pl.DataFrame()
                    c += 1
            else:
                logging.debug("Found empty file while cleaning")

    with open(os.path.join(save_path, "stats.txt"), "w") as f:
        curly_braces = "{}"
        stat_string = f"Statistiques de nettoyage:\n\nNb de phrases: {nb_sent}\nNb de phrases supprimées (total) {nb_sent-nb_cleaned_sent}\n% de phrases supprimées: {round((nb_sent-nb_cleaned_sent)/nb_sent*100, 4)}%\n\nNb de phrases supprimées (barre |): {nb_of_removed_pipes} soit {round((nb_of_removed_pipes)/nb_sent*100, 4)}%\nNb de phrases supprimées ({curly_braces}): {curly_braces_removal_rate} soit {round((curly_braces_removal_rate)/nb_sent*100, 4)}%\nNb de phrases supprimées ([]): {bracket_removal_rate} soit {round((bracket_removal_rate)/nb_sent*100, 4)}%\nNb de phrases supprimées (\"\"): {quotation_removal_count} soit {round((quotation_removal_count)/nb_sent*100, 4)}%\nNb de phrases supprimées (parentheses): {parenthesis_removal_rate} soit {round((parenthesis_removal_rate)/nb_sent*100, 4)}%\nNb de phrases supprimées (file_tags): {remove_file_tags} soit {round((remove_file_tags)/nb_sent*100, 4)}%\nNb de phrases supprimées (ending_with_cap_removal_rate): {ending_with_cap_removal_rate} soit {round((ending_with_cap_removal_rate)/nb_sent*100, 4)}%\nNb de phrases égaux: {equal_pairs} soit {round((equal_pairs)/nb_cleaned_sent*100, 4)}%"
        f.write(stat_string + f"\nTotal cleaning time: {round(time.time() - start_time)}s")


def get_global_stats(source: str):
    nb_sent = 0
    deleted_sent = 0
    nb_of_removed_pipes = 0
    curly_braces_removal_rate = 0
    bracket_removal_rate = 0
    quotation_removal_count = 0
    parenthesis_removal_rate = 0
    remove_file_tags = 0
    ending_with_cap_removal_rate = 0

    result_path =os.path.join(source, "Global_stats")
    try:
        os.mkdir(result_path)
    except FileExistsError:
        logging.warning(f"Saving the cleaned dataset in an already existing directory ({result_path}). Be shure this does not overwrite existing files.")

    files = get_file_names(source, extension=".txt")
    if not len(files):
        logging.debug("No statistic files detected to make global statistics")
        return None
    
    for file in files:
        with open(file) as f:
            content = f.read()
            stats = re.findall(r"[0-9.]+", content)
            for i, stat in enumerate(stats):
                i += 1
                if i == 1:
                    nb_sent += int(stat)
                elif i == 2:
                    deleted_sent += int(stat)
                elif i == 4:
                    nb_of_removed_pipes += int(stat)
                elif i == 6:
                    curly_braces_removal_rate += int(stat)
                elif i == 8:
                    bracket_removal_rate += int(stat)
                elif i == 10:
                    quotation_removal_count += int(stat)
                elif i == 12:
                    parenthesis_removal_rate += int(stat)
                elif i == 14:
                    remove_file_tags += float(stat)
                elif i == 16:
                    ending_with_cap_removal_rate += int(stat)
    curly_braces = "{}"
    stat_string = f"Statistiques de nettoyage:\n\nNb de phrases: {nb_sent}\nNb de phrases supprimées (total) {deleted_sent}\n% de phrases supprimées: {round((deleted_sent)/nb_sent*100, 4)}%\n\nNb de phrases supprimées (barre |): {nb_of_removed_pipes} soit {round((nb_of_removed_pipes)/nb_sent*100, 4)}%\nNb de phrases supprimées ({curly_braces}): {curly_braces_removal_rate} soit {round((curly_braces_removal_rate)/nb_sent*100, 4)}%\nNb de phrases supprimées ([]): {bracket_removal_rate} soit {round((bracket_removal_rate)/nb_sent*100, 4)}%\nNb de phrases supprimées (\"\"): {quotation_removal_count} soit {round((quotation_removal_count)/nb_sent*100, 4)}%\nNb de phrases supprimées (parentheses): {parenthesis_removal_rate} soit {round((parenthesis_removal_rate)/nb_sent*100, 4)}%\nNb de phrases supprimées (file_tags): {remove_file_tags} soit {round((remove_file_tags)/nb_sent*100, 4)}%\nNb de phrases supprimées (ending_with_cap_removal_rate): {ending_with_cap_removal_rate} soit {round((ending_with_cap_removal_rate)/nb_sent*100, 4)}%"

    with open(result_path + "\stats.txt", mode="w") as result_file:
        result_file.write(stat_string)
        logging.debug("Successfully written global statistics.")


if __name__ == "__main__":
    # Paths:
    # Source path should be a directory composed of subdirectories which contains the csv files that are desired to be cleaned up.
    source = r"D:\data\French corpora collection\files to be processed"
    # Will copy folder structure from source to result path.
    result_path = r"D:\data\French corpora collection\Wikipedia Preprocessed Files2"

    for folder in os.listdir(source):
        data = clean_folder(os.path.join(source, folder), folder, result_path)
        # reset some variables
        nb_sent = 0
        nb_cleaned_sent = 0
        equal_pairs = 0
        nb_of_removed_pipes = 0
        curly_braces_removal_rate = 0
        bracket_removal_rate = 0
        quotation_removal_count = 0
        parenthesis_removal_rate = 0
        remove_file_tags = 0
        ending_with_cap_removal_rate = 0
    
    get_global_stats(result_path)

    logging.info(f"Done cleaning {len(source)} folders in {time.time() - start} seconds.")