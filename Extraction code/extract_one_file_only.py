"""
Instead of extracting a set of files in a directory like main.py, this script will only extract one file. Please set up the variables below.
"""
import os
import logging
from main import extract_file


# Important to modify for each extraction
i = 1
file_path = r"please set up path/frwiki-20230101-pages-meta-history5.xml-p6750114p6877656"

result_path = r"please set up result path"
logging.debug(f"Make shure that the result_path ({result_path}) does not contain already existing extracted files.")

# Some Global extraction settings.
max_revisions = 5500
min_revisions = 25
max_processes = 12
save_interval = 45*60


if not os.path.isdir(result_path):
    logging.error("Path to directory does not exist: " +  result_path)
    raise ValueError

if not os.path.exists(file_path):
    logging.error("Path to file does not exist: " +  file_path)
    raise ValueError

if not ".xml" in file_path:
    logging.warning("File doesnt seem to be an xml file")

extract_file(file_path, r"{http://www.mediawiki.org/xml/export-0.10/}", [], result_path, max_revisions=max_revisions, min_revisions=min_revisions, save_interval=save_interval, n=i)