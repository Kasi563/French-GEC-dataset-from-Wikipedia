from difflib import get_close_matches
import os
import re
from multiprocessing import pool, cpu_count
import time
import lxml.etree as etree
import pandas as pd
import logging

# Setup logging settings
logging.basicConfig(format="%(asctime)s %(levelname)-8s %(message)s", level=logging.DEBUG, datefmt="%d %H:%M:%S")


# Eexecution status variables/constants.
start = time.time()
pages_extracted = 0
total_revisions = 0
cutoff_rate = 0.7


# Processing tools
import text_processing_tools as tp
# titles
from resume_extraction import get_extracted_titles


def get_time() -> tuple[float]:
    """
    Returns the time that the program has executed since the beginning of it's execution in a tuple of format (hours, minutes, seconds, elapsed), and elapsed is the total time elapsed.
    """
    elapsed = time.time() - start
    hours = elapsed//3600
    minutes = (elapsed - hours * 3600)//60
    seconds = elapsed - minutes*60 - hours*3600

    return hours, minutes, seconds, elapsed


def file_status_update(n: int) -> None:
    """
    Keeps a record of some status information for a worker. n is the ID of the worker.
    """
    hours, minutes, seconds, elapsed = get_time()
    rate = total_revisions/elapsed
    with open(f"stat_worker_{n}.txt", "w") as f:
        f.write("Number of pages extracted: {}. \nRevisions extracted: {}.  \nTime elapsed: {}h:{}min:{}s. \nExtraction rate: {}rev/s".format(pages_extracted, total_revisions, int(hours), int(minutes), int(seconds), rate))


def save_progress(X: list[str], y: list[str], titles: list[str], timestamps: list[str], comments: list[str], save_path: str, n: int, c: int) -> None:
    """
    Saves the progress of an extraction. Is used in the extract_file function to save at a time interval the extraction progress.
    """
    # Create a DataFrame of the data.
    dataframe = pd.DataFrame([[X[i], y[i], titles[i], timestamps[i], comments[i]] for i in range(len(X))], columns=["X", "y", "title", "timestamps", "comments"])
    path = save_path + "\\" + "results_fromworker_{}_nb_{}.csv".format(n, c)
    if os.path.exists(path):
        logging.warning(f"\nOverwriting a file with the path {path}\nThe file will be overwritten.")
    dataframe.to_csv(path)
    logging.debug(f"Successfully saved results from worker {n} to path {path}")


def get_info(tag: str, element, namespace=""):
    # Tries to get the text of an attribute of element (tag)
    try:
        r = element.find(namespace + tag).text
    except AttributeError:
        if not tag == "comment":
            logging.warning("Couldn't find tag %s", tag)
        return None
    return r


def extract_page(page, namespace="", extracted_titles=[], max_revisions=1800, min_revisions=25, n=0):
    """
    Gets all the X, y pairs of a wikipedia page as well as metadata like the title of the page, the timestamps, and the comments of the user eddits.
    Args:
        - page: an xml object parsed with lxml.etree. The wikipedia page in dump format (wikitext markup).
        - namespace: the potential namespace of the page.
        - extracted_titles: a list of strings representing the titles of already extracted wikipedia pages. Will not extract the page if the title of the page is in the extracted_titles list.
        - max_revisions: maximum number of accepted revisions in a wikipedia page. Will not extract the page if the pages has more revisions than the maximum number of revisions.
        - min_revisions: minimum number of accepted revisions in a wikipedia page. Will not extract the page if the pages has less revisions than the minimum number of revisions.
        - n: id (of type int) of the worker that calls this function.
    """
    global pages_extracted
    global total_revisions
    # The results lists.
    y = []
    X = []
    titles = []
    timestamps = []
    comments = []
    title = ""

    failed = False
    first_page = True

    # get the title of the page
    try:
        title = page.find(namespace + "title")
    except TypeError:
        logging.warning("TypeError: No title found for page %s, skipping page" % page)
        title = "None"
        return X, y, title
    if title != None:
        title = title.text

    if not tp.check_title(title) and not title in extracted_titles: # Checks that the page is desirable
        revisions = page.findall(namespace + "revision")
        nb_revisions = len(revisions)

        if nb_revisions <= max_revisions or nb_revisions >= min_revisions: # Checks that the number of revisions is within the limit defined.
            for rev in page.findall(namespace + "revision"):
                text = get_info("text", rev, namespace=namespace) # Get the page text of the revision.

                if text != None:
                    text = tp.pre_cleaner(text) # Pre clean the text (remove certain wikitext markup elements for example).
                else:
                    failed = True

                if not failed:
                    if not first_page:
                        # Get revision metadata
                        timestamp1 = get_info("timestamp", rev, namespace=namespace)
                        comment = get_info("comment", rev, namespace=namespace)
                        try:
                            # Split the revision text into sentences
                            new_revision = tp.split_text(text)
                        except TypeError:
                            logging.warning("TypeError from tp.split_text. Parameter Text: %s" % text)
                            new_revision = [""]

                        new_revision_sents, old_revision_sents = tp.filter_direct_matches(new_revision, old_revision)
                        
                        for sentence in old_revision_sents:
                            # Get the closest matching sentence.
                            match = get_close_matches(sentence, new_revision_sents, n=1, cutoff=cutoff_rate)
                            if match: # If the sentence has a 'look alike' (correction)
                                try:
                                    # Clean the remaining templates and wikimarkup files.
                                    match = tp.post_cleaner(match[0][2:])
                                    sentence = tp.post_cleaner(sentence[2:])
                                except AttributeError:
                                    logging.warning(f"AttributeError: Failed to clean the pairs of sentences: match: {match} sentence: {sentence}")
                                    match = False
                                if match and not match == sentence:
                                    # Save the sentence to the results lists.
                                    y.append(re.sub(r'\n', '', match))
                                    X.append(re.sub(r"\n", "", sentence))
                                    titles.append(title)
                                    timestamps.append(timestamp1 + " " + timestamp2)
                                    comments.append(comment)
                        
                        # Set the new revision to the old revision.
                        timestamp2 = timestamp1
                        old_revision = new_revision

                    else:
                        # This code executes if the revision is the first revision of the page.
                        old_revision = tp.split_text(text)
                        timestamp2 = get_info("timestamp", rev, namespace=namespace)
                        first_page = False
                else:
                    failed = False
                rev.clear() # Clear the revision from memory
            
            total_revisions += nb_revisions
        pages_extracted += 1

    if pages_extracted % 2:
        file_status_update(n)
    page.clear()

    return X, y, titles, timestamps, comments


def extract_file(file_path: str, namespace: str, extracted_titles: list, save_path: str, max_revisions=1800, min_revisions=25, n=0, save_interval=3600) -> None:
    """
    Function to extract whole wikipedia dumps (.xml files). Saves the extracted sentences (X, y pairs) to save_path in csv format every save_interval (in seconds) with columns: 'X', 'y', 'timestamp', 'title', 'comments'.

    Args:
        - file_path: complete path to the wikipedia dump .xml file to extract.
        - namespace: the namespace of the .xml file if it has one.
        - extracted_title: a list of already extracted wikipedia pages so that the program can resume extracting from where it left off. If first time extracting the file, should be an empty list.
        - save_path: a directory for saving the results of the extraction.
        - max_revisions: maximum number of accepted revisions in a wikipedia page.
        - min_revisions: minimum number of accepted revisions in a wikipedia page.
        - n: id of the worker. Important to be different from the other workers if using multiprocessing.
        - save_interval: how often to save the results of the extraction in seconds.
    """

    logging.info(f"Starting extraction of file: {file_path} with worker number: {n}")

    # Set some variables

    # results:
    X = []
    y = []
    titles = []
    timestamps = []
    comments = []

    c = 0 # count for the number of saves (rename)
    if extracted_titles:
        resumed = False
    else:
        resumed = True

    try:
        for _, elem in etree.iterparse(file_path, tag=namespace + 'page'): # Using the iterparse to be able to handle huge files.
            X_, y_, titles_, timestamps_, comments_ = extract_page(elem, namespace, extracted_titles, max_revisions, min_revisions, n)

            if not X == [] and not resumed: # Checks if we have resumed resumed from where we left off
                extracted_titles = []
                resumed = True
                logging.info(f"resumed with worker: {n}")

            for i in range(len(titles_)): # Destructure and add the results from the extract_page function to the main results variables.
                X.append(X_[i])
                y.append(y_[i])
                titles.append(titles_[i])
                timestamps.append(timestamps_[i])
                comments.append(comments_[i])

            if (time.time() - start) > save_interval:
                # Save the collected data in the files
                save_progress(X, y, titles, timestamps, comments, save_path, n, c)
                c += 1
                save_interval = save_interval*2

                # Reset the results variables
                X = []
                y = []
                titles = []
                timestamps = []
                comments = []

    except etree.XMLSyntaxError as e:
        # This is a newly detected problem that I can't seem to see a fix.
        # In the middle of the extraction, the parser encounters some times a special utf-8 character that causes it to raise an error.
        # Temporary try except statement so that the exctracion of the rest of the files doesn't break.
        logging.error(f"ERROR WITH iterparse for worker {n}: {e}")

    # Final save
    save_progress(X, y, titles, timestamps, comments, save_path, n, c)
    # Delete the wikipedia dump file after it has been completely extracted.
    logging.info(f"Done extracting. Deleting file: {file_path}")
    os.remove(file_path)


def exctraction_report(time: str, files_paths: str, results_path: str, max_revisions: int, min_revisions: int) -> None:
    """
    Creates .txt file that reports some information about the complete extraction of the extracted files.
    Takes as arguments all the important parameters used in the extraction and the execution time.
    """
    with open(results_path + r"\report.txt", "w") as f:
        text = "Extraction report: \n\n" + time + f"\nMax_revisions: {max_revisions}\nMin_revisions: {min_revisions}\nFiles extracted: "
        for file_path in files_paths:
            text = text + " " + file_path
        text += f"\nNumber of files extracted: {len(files_paths)}"
        f.write(text)


if __name__ == "__main__":
    # Execution parameters:
    extraction_directory = r"some_path\files_to_extract"
    result_directory = r"some_path\Extraction11"
    namespace = r"{http://www.mediawiki.org/xml/export-0.10/}" # If xml files has namespaces
    max_revisions = 5500
    min_revision = 25
    num_processes = 12 # Number of parallel processes (number of cpu cores)
    save_interval = 45*60 # in seconds: every 45 minutes
    resume_path = None

    # If num_processes exceeds maximum hardware limit (number of cpu cores), resets it to the number of cores available:
    max_cpu = cpu_count()
    if num_processes > cpu_count():
        logging.info(f"num_proceses exceeds maximum number of cpu cores on the system. Setting num_process from {num_processes} to {max_cpu}")
        num_processes = max_cpu

    # If resume path is a path, checks if it exists.
    if resume_path:
        if not os.path.isdir(resume_path):
            logging.error("Path to directory does not exist: " +  resume_path)
            raise ValueError

    # Checks if extraction_directory directory exists
    if not os.path.isdir(extraction_directory):
        logging.error("Path to directory does not exist: " +  extraction_directory)
        raise ValueError
    
    if not os.path.isdir(result_directory):
        logging.error("Path to directory does not exist: " +  result_directory)
        raise ValueError

    # If resume_path is specified, then all the titles from the last exctraction stored in resume_path will be stored in titles list.
    if resume_path:
        titles = get_extracted_titles(resume_path)
        if titles:
            logging.info("Done loading resume data from %s", resume_path)
            logging.info("Number of titles extracted: %s", len(titles))

    # Get all the wikipedia dump files (.xml):
    files_to_extract = os.listdir(extraction_directory)
    if len(files_to_extract) == 0:
        logging.warning("Couldn't find files in this directory: " + extraction_directory)

    # We get the full path to all of the wikipedia dump files:
    source_xml_files = []
    for file_path in files_to_extract:
        if file_path.endswith(".xml"):
            source_xml_files.append(extraction_directory + "\\" + file_path)

    # Selects the files to extracts if there are too many.
    if len(source_xml_files) > num_processes:
        source_xml_files = source_xml_files[:num_processes]
        logging.info(f"Cannot extract more than '{num_processes}' files at a time (num_processes) due to hardware limitations. Will only extract the first 8 files: {source_xml_files}")

    extraction_pool = pool.Pool(num_processes)
    try:
        # Starting the extraction by calling the extract_file function with pool for every file to extract.
        extraction_pool.starmap(extract_file, [(source_xml_files[i], namespace, titles, result_directory, max_revisions, min_revision, i, save_interval) for i in range(len(source_xml_files))])
    except TypeError:
        logging.error("There is a huge type error in main file extraction_pool.startmap method!!!")

    # Display final info & results
    hours, minutes, seconds, elapsed = get_time()
    formatted_time = "Complete execution time: {}h:{}min:{}s tot: {}.".format(int(hours), int(minutes), int(seconds), round(elapsed))
    logging.info(f"Total extraction time: {formatted_time}")
    exctraction_report(formatted_time, files_to_extract, result_directory, max_revisions, min_revision)
    logging.info("EXECUTION COMPLETE.")