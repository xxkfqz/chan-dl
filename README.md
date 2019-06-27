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

    chan-dl.py [-h] [-o] [-d DIR] [-z] [-Z] [-q] [-s] [-v] [--no-stderr]
               URL [URL ...]

    positional arguments:
      URL                   url to thread

    optional arguments:
      -h, --help            show this help message and exit
      -o, --overwrite       overwrite existing files
      -d DIR, --dir DIR     output directory
      -z, --zip             create *.zip arhive after downloading
                            (previous one will be removed if exists)
      -Z, --only-zip        delete downloaded files after archiving
                            (includes -z)
      -q, --quiet           do not print anything
      -s, --skip-failed     just skip downloading failed URL instead quit
      -v, --verbose         be a little verbose
      --no-stderr           disable stderr messages (do not disables tracebacks)

# Examples

    # Just download all pictures and videos to current directory
    ./chan-dl.py http://boards.4chan.org/c/thread/1990691

    # Multiple URLs
    ./chan-dl.py boards.4chan.org/w/thread/1565459 2ch.hk/pr/res/1008826.html#1008826

    # Create a ZIP archive after download. Put everything at '~/pictures'
    ./chan-dl.py http://boards.4channel.org/c/thread/3475819 -d ~/pictures
