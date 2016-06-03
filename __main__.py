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

args = args_parser.parse_args()
searcher = Searcher()
start_time = time.time()

count = 0
result = searcher.search_for_pattern(args.directory, args.regex_pattern)
with open(args.output_file, 'w+b') as file:
    for res in result:
        count += len(res)
        file.writelines(res)

end_time = time.time()
print('time elapsed:')
utils.print_elapsed_time(start_time=start_time, end_time=end_time)
print('#### found {0!s} matching line(s) ####'.format(count))
print('done!')
