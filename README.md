# chan-dl.py

Script for downloading media files from imageboards using their API

# Supported imageboards

* [4chan](http://4chan.org)
* [2ch](https://2ch.hk)
* [Dobrochan](http://dobrochan.org)
* [Tumbach](https://tumba.ch)
* [Lolifox](https://lolifox.org)

# Dependecies

`apt install python3-requests`

or

`pip3 install requests`

# Usage

	chan-dl.py [-h] [-o] [-d DIRECTORY] [-q] [--no-stderr] URL [URL ...]

	positional arguments:
	  URL              url to thread

	optional arguments:
	  -h, --help            show this help message and exit
	  -o, --overwrite       overwrite existing files
	  -d DIR, --dir DIR     output directory
	  -z, --zip             create *.zip arhive after downloading
	                        (previous one will be removed if exists)
	  -Z, --only-zip        delete downloaded files after archiving
	  -q, --quiet           do not print anything
	  --no-stderr           disable stderr messages (do not disables tracebacks)

# Examples

	./chan-dl.py http://boards.4chan.org/c/thread/1990691

	./chan-dl.py boards.4chan.org/w/thread/1565459 2ch.hk/pr/res/1008826.html#1008826 -o -d ~/pictures/ -zZ
