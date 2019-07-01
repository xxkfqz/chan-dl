# chan-dl.py

Script for downloading media files from imageboards using their API

# Supported imageboards

* [4chan](https://4chan.org)
* [2ch](https://2ch.hk)
* [Dobrochan](http://dobrochan.org)
* [Tumbach](https://tumba.ch)
* [Lolifox](https://lolifox.org)

# Dependecies

* [Python 3](https://python.org)
* [requests](https://python-requests.org)

# Usage

    chan-dl.py [-h] [-o] [-f START_INDEX] [-t END_INDEX] [-d DIR] [-m] [-c]
               [-z] [-Z] [-q] [-s] [-v] [--no-stderr] URL [URL ...]

    Download media files from imageboards

    Supported imageboards:
     * 4chan
     * 2ch
     * Dobrochan
     * Tumbach
     * Lolifox

    positional arguments:
      URL                   url to thread

    optional arguments:
      -h, --help            show this help message and exit
      -o, --overwrite       overwrite existing files
                            (does not works with -m)
      -f START_INDEX, --from START_INDEX
                            start of range mediafiles number (default: 1)
      -t END_INDEX, --to END_INDEX
                            end of range mediafiles number (default: none)
      -d DIR, --dir DIR     output directory
      -m, --md5             change filenames to MD5 hash
      -c, --check           check files for duplicating via MD5
                            (like -m option but without renaming)
      -z, --zip             create *.zip archive after downloading
                            (previous one will be removed if exists)
      -Z, --only-zip        delete downloaded files after archiving
                            (includes -z)
      -q, --quiet           do not print anything
      -s, --skip-failed     just skip downloading failed URL instead quit
      -v, --verbose         be a little verbose
      --no-stderr           disable stderr messages (do not disables tracebacks)

# Examples

    # Just download all pictures and videos to current directory
    chan-dl.py http://boards.4chan.org/c/thread/1990691

    # Multiple URLs
    chan-dl.py boards.4chan.org/w/thread/1565459 2ch.hk/pr/res/1008826.html#1008826

    # Create a ZIP archive after download. Put everything at '~/pictures'
    chan-dl.py http://boards.4channel.org/c/thread/3475819 -d ~/pictures

    # Download only 10-15 files from thread and check them for duplications
    chan-dl.py http://boards.4chan.org/c/thread/1990691 -f 10 -t 15 -c
