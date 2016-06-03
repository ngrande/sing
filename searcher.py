import os
import re
import io
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor


class Searcher:
    def __init__(self):
        pass

    def _generate_file_searchers(self, directory, pattern):
        """ scan the whole directory + subdirectories for fiels """
        # if directory is actually only a single file
        if os.path.isfile(directory):
            yield FileSearcher(directory, pattern)
        else:
            # else scan all files in the directory + subdirectories
            for file_name in os.listdir(directory):
                temp_file_path = directory + '/' + file_name
                if os.path.isdir(temp_file_path):
                    # if file is a directory -> recursive call to itself
                    for fs in self._generate_file_searchers(temp_file_path,
                                                            pattern):
                        yield fs
                else:
                    yield FileSearcher(temp_file_path, pattern)

    def search_for_pattern(self, directory, pattern):
        """ starts the search for all files in the directory for the pattern
        - uses a thread pool (as set in the constructor) """
        print('search started...')
        processes = []
        with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as p:
            for searcher in self._generate_file_searchers(directory, pattern):
                processes.append(p.submit(searcher.search_in_file))
            for async_proc in processes:
                yield async_proc.result()


class FileSearcher:
    """ used to search in a single file """
    def __init__(self, file_path, pattern):
        self.file_path = file_path
        self.pattern = pattern.encode('utf-8')
        self.pattern_search = re.compile(self.pattern).search
        # chunk_size is a multiple of the default buffer size to ensure that it
        # is worth spawning multiple threads for a single file
        # => One chunk is big enough to be processed within a reasonable time
        # and avoids too much overhead
        self.chunk_size = io.DEFAULT_BUFFER_SIZE * 8192

    def _search_part_in_file(self, start_pos, end_pos):
        """ searches a regex pattern in a specified part of a file """
        # temp_result = []
        # buffer_size = end_pos - start_pos + 1
        with open(self.file_path, mode='rb',
                  buffering=self.chunk_size) as file:
            # check if this line is complete by looking for the \n
            # (checks if this pos is the beginning of a new line)
            is_complete_line = start_pos is 0
            if start_pos > 0:
                file.seek(start_pos - 1)
            if not is_complete_line and file.read(1) is b'\n':
                is_complete_line = True

            # initial set the start pos
            file.seek(start_pos)

            first = True
            for line in file.readlines(end_pos - start_pos):
                if first and not is_complete_line:
                    first = False
                elif self.pattern_search(line) is not None:
                    yield line

    def search_in_file(self):
        """ searches regex pattern in complete file - will create multiple
            threads (if necessary) to search simultanously in a single file """
        file_size = os.path.getsize(self.file_path)
        threads = []
        results = []

        with ThreadPoolExecutor() as e:
            for position in self._calculate_positions(file_size):
                threads.append(e.submit(self._search_part_in_file, position[0], position[1]))
            for thread in threads:
                results.extend(thread.result())
        return results

    def _calculate_positions(self, file_size):
        """ divides the file into chunks and returns position pairs
        (start + end) for the parts to search in the file """
        if file_size >= self.chunk_size:
            # how many times the chunk_size fits into the file size
            div = int(file_size / self.chunk_size)
            # the rest which does not fit anymore
            rest = file_size % self.chunk_size
            last_end_pos = None
            for i in range(0, div):
                start_pos = i * self.chunk_size
                # add a -1 => otherwise it will begin where the prev ended
                end_pos = start_pos + (self.chunk_size)
                last_end_pos = end_pos
                yield [start_pos, end_pos]
            # add the rest + 1 because last has the -1
            yield [last_end_pos, last_end_pos + rest]
        else:
            yield [0, file_size]
