import os
import re
import threading
import io
from concurrent.futures import ThreadPoolExecutor

# TODO: shutdown the executor (or using the 'with' keyword properly)


class Searcher:
    def __init__(self, max_concurr_threads=10):
        self.max_concurr_threads = max_concurr_threads
        self.file_searchers = []

    def search_for_pattern_async(self, directory, pattern):
        """ search all files in the directory of this object for the pattern.
        """
        print('search in directory {0!s} started'.format(directory))

        # if directory is actually only a single file
        if os.path.isfile(directory):
            self._add_file_searcher(directory, pattern)
            return

        # else scan all files in the directory + subdirectories
        for file_name in os.listdir(directory):
            temp_file_path = directory + '/' + file_name
            if os.path.isdir(temp_file_path):
                # if file is a directory -> recursive call to itself
                self.search_for_pattern_async(temp_file_path, pattern)
            else:
                self._add_file_searcher(temp_file_path, pattern)

    # def _search_callback(self, result):
        # self.thread_count -= 1
        # self.all_results.extend(result)

    def _add_file_searcher(self, file_path, pattern):
        file_searcher = FileSearcher(file_path, pattern)
        self.file_searchers.append(file_searcher)

    def wait_for_results(self):
        self.all_results = []
        self.count_left = len(self.file_searchers)
        with ThreadPoolExecutor(max_workers=self.
                                max_concurr_threads) as executor:
            for searcher in self.file_searchers:
                executor.submit(self.do_it, searcher)

        return self.all_results

    def do_it(self, searcher):
        self._update_terminal(self.count_left)
        self.all_results.extend(searcher.
                                search_in_file(self.max_concurr_threads))
        self.count_left -= 1
        # print(len(self.all_results))
        self._update_terminal(self.count_left)

    def _update_terminal(self, count_left):
        # nt => Windows (New Technologie)
        os.system('cls' if os.name == 'nt' else 'clear')
        print('waiting for {0!s} filescan(s) to finish.'
              .format(count_left))


class FileSearcher:
    def __init__(self, file_path, pattern):
        self.file_path = file_path
        self.pattern = pattern.encode('utf-8')
        self.file_results = []
        # junk_size is a multiple of the default buffer size to ensure that it
        # is worth spawning multiple threads for a single file
        self.junk_size = io.DEFAULT_BUFFER_SIZE * 2048

    def _search_part_in_file(self, start_pos, end_pos):
        temp_result = []
        # buffer size = end_pos because so everything that is needed will be
        # read at once
        buffer_size = end_pos  # (end_pos - start_pos) * 2
        with open(self.file_path, mode='rb',
                  buffering=self.junk_size + 1) as file:
            # check if this line is complete by looking for the \n
            # (checks if this pos is the beginning of a new line)
            is_new_line = start_pos is 0
            if start_pos > 0:
                file.seek(start_pos - 1)
            if not is_new_line and file.read(1) is b'\n':
                is_new_line = True

            # initial set the start pos
            file.seek(start_pos)

            lines = file.readlines(end_pos - start_pos)
            if not is_new_line and len(lines) > 0:
                # throw away the first if it is not the beginning of a new line
                # line = file.readline()
                del lines[0]

            # curr_pos = 0
            # while curr_pos < end_pos:
            for bline in lines:
                # bline = file.readline()
                # curr_pos = file.tell()
                # binary regex
                match = re.search(self.pattern, bline)
                if (match is not None):
                    temp_result.append(bline)

        self.file_results.extend(temp_result)

    def search_in_file(self, max_concurr_threads):
        self.file_results = []
        file_size = os.path.getsize(self.file_path)
        positions = self._calc_positions(file_size)  # , max_concurr_threads)

        with ThreadPoolExecutor() as executor:
            for pos in positions:
                executor.submit(self._search_part_in_file, pos[0], pos[1])

        return self.file_results

    def _calc_positions(self, file_size):
        results = []

        if file_size >= self.junk_size:
            # how many times the junk_size fits into the file size
            div = int(file_size / self.junk_size)
            # the rest which does not fit anymore
            rest = file_size % self.junk_size
            for i in range(0, div):
                temp_pos = i * self.junk_size
                # add a -1 => otherwise it will begin where the prev ended
                results.append([temp_pos, temp_pos +
                               (self.junk_size - 1)])
            # add the rest + 1 because last has the -1
            last = results[len(results) - 1][1]
            results.append([last, last + rest + 1])
        else:
            results.append([0, file_size])
        return results
