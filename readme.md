# Sing
acronym for **S**ing **i**s **n**ot **g**ood

Sing is an easy to use search tool. You can search all files in a directory and its subdirectories using regular expressions.

__BUT__: It is _slow_ as it is _simple_. Not recommend to use for fast searching.

## Usage
### simple search in the current directory
`$python sing -p "SomeRegex"`

### specify output file
`$python sing -p "SomeRegex" -o "~/matching_lines"`

### ...and a directory
`$python sing -p "non-free" -d "/etc/apt/"`
