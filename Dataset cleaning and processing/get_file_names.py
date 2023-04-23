"""
A function used by multiple files.
"""
import os

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
