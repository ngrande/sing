import argparse
import io
import time
import utils
from searcher import Searcher


args_parser = argparse.ArgumentParser(description='Search all files in a '
                                      'directory (including subdirectories) '
                                      'for a regex pattern')
args_parser.add_argument('-p', '--regex-pattern', help='regex pattern to '
                         'search for in the file(s) in the directory',
                         required=True)
args_parser.add_argument('-o', '--output-file', nargs='?', help='path to the '
                         'output file where all matching lines will be written'
                         ' to', default='matches.txt', type=str)
args_parser.add_argument('-d', '--directory', nargs='?', type=str,
                         help='directory of file(s) which will be scanned',
                         default='./')
args_parser.add_argument('-n', '--number-of-threads', nargs='?', type=int,
                         help='maximum number of concurrent threads used to '
                         'scan the files (does only limit how many files are '
                         'scanned simultanously - not the actual number of '
                         'threads)', default=10)

args = args_parser.parse_args()
searcher = Searcher(args.number_of_threads)
start_time = time.time()
matching_lines = searcher.search_for_pattern(args.directory,
                                             args.regex_pattern)
# matching_lines = searcher.wait_for_results()
end_time = time.time()

print('time elapsed:')
utils.print_elapsed_time(start_time=start_time, end_time=end_time)
print('#### found {0!s} matching line(s) ####'.format(len(matching_lines)))
if len(matching_lines) > 0:
    print('writing matching lines into output file... (may take a second)')
    with open(args.output_file, 'w+b') as file:
        file.writelines(matching_lines)
print('done!')
