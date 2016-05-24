import os
import re
import threading
from concurrent.futures import ThreadPoolExecutor


class Searcher:
    def __init__(self):
        self.thread_count = 0
        self.all_results = []
        self.thread_count_before = self.thread_count
        # self.executor = ThreadPoolExecutor(max_workers=10)

    def search_for_pattern_async(self, directory, pattern):
        """ search all files in the directory of this object for the pattern.
        Returns list of matching strings (lines in the file). If live is
        set to true it will directly print the output to the console. """
        self.thread_count = 0
        self.all_results = []
        print('search in directory {0!s} started'.format(directory))

        # if directory is actually only a single file
        if os.path.isfile(directory):
            self._start_search_thread(directory, pattern)

        # else scan all files in the directory + subdirectories
        for file_name in os.listdir(directory):
            temp_file_path = directory + '/' + file_name
            if os.path.isdir(temp_file_path):
                # if file is a directory -> recursive call to itself

                # ATTENTION! Recursive call is not yet threaded
                self.search_for_pattern_async(temp_file_path, pattern)
            else:
                self._start_search_thread(temp_file_path, pattern)

        return self._wait_for_results()

    def _search_callback(self, result):
        # print('search callback invoked')
        self.thread_count -= 1
        self.all_results.extend(result)

    def _start_search_thread(self, file_path, pattern):
        # print('starting search thread')
        thread = SearchThread()
        self.thread_count += 1
        thread.search_in_file_async(file_path, pattern, self._search_callback)

    def _wait_for_results(self):
        while self.thread_count > 0:
            self._update_terminal()
        return self.all_results

    def _update_terminal(self):
        if (self.thread_count is not self.thread_count_before):
            # nt => Windows (New Technologie)
            os.system('cls' if os.name == 'nt' else 'clear')
            print('waiting for {0!s} thread(s) to finish.'
                  .format(self.thread_count))
            self.thread_count_before = self.thread_count


class SearchThread:
    def __init__(self):
        self.search_thread = None
        self.search_callback = None

    def _search_in_file(self, file_path, pattern):
        temp_result = []
        for line in open(file_path, mode='r', errors='replace'):
            match = re.search(pattern, line)
            if (match is not None):
                temp_result.append(line)

        if self.search_callback is not None:
            # print('file search finished - invoking callback')
            self.search_callback(temp_result)

    def search_in_file_async(self, file_path, pattern, search_callback):
        self.search_callback = search_callback
        self.search_thread = threading.Thread(target=self._search_in_file,
                                              args=(file_path, pattern))
        self.search_thread.start()
        # print('searchThread started')
        # return self.search_thread
