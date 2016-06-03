# SINT
**S**earch **I**n **N**o **T**ime

SINT is an easy to use search tool. You can search all files in a directory and its subdirectories (or just a single file) using regular expressions and save the matching lines in an output file. Useful if you are looking for error messages in many log files. The script is for now optimized for search over a bunch of smaller (each ~10 MiB) files. The single file search performance is not quite as good as the directory search.

__High Score:__ ~__10 Seconds__ to scan __3.5 GB__ of files (8 MiB per file) (Intel i7-2630QM + SanDisk SSD)


## Usage
### simple search in the current directory
`$python sint -p "SomeRegex"`

### specify output file
`$python sint -p "SomeRegex" -o "~/matching_lines"`

### ...and a directory
`$python sint -p "non-free" -d "/etc/apt/"`

### an advanced example
`$python sint -p "error" -o "/home/me/matching_lines" -d "/var/log/syslog"`

## Help is on the way!
just type `$python sint -h`
