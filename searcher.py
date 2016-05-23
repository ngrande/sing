import os
import re

# todo: add multithreading for faster file scanning


def search_pattern(directory, pattern, live=True):
    """ search all files in the directory of this object for the pattern.
    Returns list of matching strings (lines in the file). If live is
    set to true it will directly print the output to the console. """
    temp_results = []

    # if directory is actually only a single file
    if os.path.isfile(directory):
        return search_file(directory, pattern, live)

    # else scan all files in the directory + subdirectories
    for file_name in os.listdir(directory):
        temp_file_path = directory + '/' + file_name
        if os.path.isdir(temp_file_path):
            # if file is a directory -> recursive call to itself
            temp_results.extend(search_pattern(temp_file_path, pattern, live))
        else:
            if live:
                print('scanning file "{0!s}"...'.format(temp_file_path))
            temp_results.extend(search_file(temp_file_path, pattern, live))

    return temp_results


def search_file(path, pattern, live=True):
    file_match_counter = 0
    temp_results = []
    for line in open(path, mode='r', errors='replace'):
        # print(line)
        match = re.search(pattern, line)
        if (match is not None):
            file_match_counter += 1
            temp_results.append(line)
            if live:
                print(line)
    if live:
        print('found {0!s} matching line(s) in this file!'
              .format(file_match_counter))

    return temp_results
