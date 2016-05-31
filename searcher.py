import os
import re
import threading
from concurrent.futures import ThreadPoolExecutor


class Searcher:
    def __init__(self, max_concurr_threads=10):
        self.thread_count = 0
        self.all_results = []
        self.thread_count_before = self.thread_count
        self.executor = ThreadPoolExecutor(max_workers=max_concurr_threads)

    def search_for_pattern_async(self, directory, pattern):
        """ search all files in the directory of this object for the pattern.
        """
        print('search in directory {0!s} started'.format(directory))

        # if directory is actually only a single file
        if os.path.isfile(directory):
            self._start_search_thread(directory, pattern)
            return

        # else scan all files in the directory + subdirectories
        for file_name in os.listdir(directory):
            temp_file_path = directory + '/' + file_name
            if os.path.isdir(temp_file_path):
                # if file is a directory -> recursive call to itself
                self.search_for_pattern_async(temp_file_path, pattern)
            else:
                self._start_search_thread(temp_file_path, pattern)

    def _search_callback(self, result):
        self.thread_count -= 1
        self.all_results.extend(result)

    def _start_search_thread(self, file_path, pattern):
        thread = SearchThread(self.executor)
        self.thread_count += 1
        thread.search_in_file_async(file_path, pattern, self._search_callback)

    def wait_for_results(self):
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
    def __init__(self, threadpool_exec):
        self.search_thread = None
        self.search_callback = None
        self.threadpool_exec = threadpool_exec
        self.max_file_junk_size = 5242880  # bytes => 5 MiB

    def _search_in_file(self, file_path, pattern, start_pos, end_pos):
        temp_result = []
        for line in open(file_path, mode='r', errors='replace'):
            match = re.search(pattern, line)
            if (match is not None):
                temp_result.append(line)

        if self.search_callback is not None:
            self.search_callback(temp_result)

    def search_in_file_async(self, file_path, pattern, search_callback):
        self.search_callback = search_callback
        self.threadpool_exec.submit(self._search_in_file, file_path, pattern)

    def _calc_positions(self, file_path):
        size = os.path.getsize(file_path)
        if size >= self.max_file_junk_size:
            div = int(size / self.max_file_junk_size)  # how many times the max_file_junk_size fits into the file size
            rest = size % self.max_file_junk_size  # the rest which does not fit anymore
            results = []
            for i in range(0, div):
                temp_pos = i * self.max_file_junk_size
                # add a -1?
                results.append((temp_pos, temp_pos + self.max_file_junk_size))
            # add the rest
            last = results[len(results) - 1]
            results.append((last, last+rest))
            # not done yet...
