# dirsplitter

Split large directories into parts of a specified maximum size. This is a python port of my dirsplitter tool.

[F# Version](https://github.com/jinyus/fs_dirsplitter) (more binaries available)<br>
[nim Version](https://github.com/jinyus/nim_dirsplitter)<br>
[Go version](https://github.com/jinyus/dirsplitter)<br>
[Crystal Version](https://github.com/jinyus/cr_dirsplitter)

How to run

```
pip install -r reqs.txt
python dirsplitter.py
```

## create an alias for convenience:

```bash
alias dirsplitter='python /path/to/dirsplitter.py'
```

## USAGE:

```text
dirsplitter.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  reverse
  split
  version
```

## SPLIT USAGE:

```text
Splits directory into a specified maximum size

Usage:
dirsplitter.py split [OPTIONS] [DIRECTORY]

Options:
  -m, --max FLOAT    Size of each part in GB  [default: 5.0]
  -p, --prefix TEXT  Prefix for output files of the tar command. eg:
                     myprefix.part1.tar
  --help             Show this message and exit.
```

### example:

```text
dirsplitter split --max 0.5 ./mylarge2GBdirectory

This will yield the following directory structure:

📂mylarge2GBdirectory
 |- 📂part1
 |- 📂part2
 |- 📂part3
 |- 📂part4

with each part being a maximum of 500MB in size.
```

Undo splitting

```
dirsplitter reverse ./mylarge2GBdirectory

```
