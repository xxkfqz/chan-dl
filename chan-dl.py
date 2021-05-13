#!/usr/bin/env python3
# Copyleft by xxkfqz <xxkfqz@gmail.com> 2d18-2d19

import signal
import sys
import os
from hashlib import md5

import argparse
import zipfile
try:
    import urllib3
    import requests
except ImportError:
    # RTFM
    print('Module "requests" not found. See README.md for details')
    sys.exit(-1)

# Delete unfinished file when got a SIGINT
journal_path = ''

# Will be used by 'progress_sym'
sym_number = 0

# Will be used if we want to check duplications
sum_list = {}

downloaded_files = 0

def print_c(*args, **kargs):
    if cliargs.quiet:
        return

    print(*args, **kargs)
    sys.stdout.flush()

def print_verbose(*args, **kargs):
    if cliargs.verbose:
        print_c(*args, *kargs)

def progress_sym(clear = False):
    if cliargs.quiet:
        return

    global sym_number
    symbols = '/-\\|'
    print('\b' + symbols[sym_number % len(symbols)], end='')
    sym_number += 1
    sys.stdout.flush()

def errexit(msg):
    if not cliargs.no_stderr:
        sys.stderr.write(msg + '\n')
    sys.exit(-1)

def sigint_handler(sig, frame):
    if journal_path != '':
        os.remove(journal_path)
    errexit('\n> Caught SIGINT <')

def init_parser():
    parser = argparse.ArgumentParser(
        description = '''
Download media files from imageboards

Supported imageboards:
 * 4chan
 * 2ch
 * Dobrochan
 * Tumbach
 * Lolifox
''',
        add_help = True,
        formatter_class = argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        '-o',
        '--overwrite',
        action = 'store_true',
        help = 'overwrite existing files\n(does not works with -m)'
    )
    parser.add_argument(
        '-f',
        '--from',
        dest = 'start_index',
        help = 'start of range mediafiles number (default: 1)'
    )
    parser.add_argument(
        '-t',
        '--to',
        dest = 'end_index',
        help = 'end of range mediafiles number (default: none)'
    )
    parser.add_argument(
        '-d',
        '--dir',
        help = 'output directory'
    )
    parser.add_argument(
        '-m',
        '--md5',
        action = 'store_true',
        help = 'change filenames to MD5 hash'
    )
    parser.add_argument(
        '-c',
        '--check',
        action = 'store_true',
        help = 'check files for duplicating via MD5\n(like -m option but without renaming)'
    )
    parser.add_argument(
        '-z',
        '--zip',
        action = 'store_true',
        help = 'create *.zip archive after downloading\n(previous one will be removed if exists)'
    )
    parser.add_argument(
        '-Z',
        '--only-zip',
        action = 'store_true',
        help = 'delete downloaded files after archiving\n(includes -z)'
    )
    parser.add_argument(
        '-q',
        '--quiet',
        action = 'store_true',
        help = 'do not print anything'
    )
    parser.add_argument(
        '-s',
        '--skip-failed',
        action = 'store_true',
        help = 'just skip downloading failed URL instead quit'
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action = 'store_true',
        help = 'be a little verbose'
    )
    parser.add_argument(
        '--no-stderr',
        action = 'store_true',
        help = 'disable stderr messages (do not disables tracebacks)'
    )

    parser.add_argument(
        'urls',
        metavar = 'URL',
        nargs = '+',
        type = str,
        help = 'url to thread'
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(-1)
    return parser.parse_args()

def parse_api(chan, board, response):
    u = []
    f = []
    if chan == '4chan':
        for p in response['posts']:
            if not 'tim' in p:
                continue
            tim = p['tim']
            ext = p['ext']
            u.append('https://i.4cdn.org/{}/{}{}'.format(board, tim, ext))
            f.append('{}{}'.format(tim, ext))
    elif chan == '2ch':
        for p in response:
            for files in p['files']:
                u.append('https://2ch.hk/' + files['path'])
                f.append(files['name'])
    elif chan == 'dobrochan':
        for p in response['result']['threads'][0]['posts']:
            for files in p['files']:
                s = files['src']
                u.append('http://dobrochan.ru/' + s)
                filename = s.split('/')[3]
                f.append(filename)
    elif chan == 'tumbach':
        res_url = 'https://tumba.ch/{}/src/{}'
        # OP's post
        for p in response['thread']['opPost']['fileInfos']:
            u.append(res_url.format(board, p['name']))
            f.append(p['name'])
        # The rest of thread
        for p in response['thread']['lastPosts']:
            if not p['fileInfos']:
                continue
            for k in p['fileInfos']:
                u.append(res_url.format(board, k['name']))
                f.append(k['name'])
    elif chan == 'lolifox':
        for p in response['posts']:
            u.append(res_url.format(board, p['tim'], p['ext']))
            f.append('{}{}'.format(p['tim'], p['ext']))

    return u, f

def get_media_urls(raw_url):
    s = raw_url.split('/')
    if s[0] == 'http:' or s[0] == 'https:':
        s.pop(0)
        s.pop(0)

    # 4chan
    if s[0] == 'boards.4chan.org' or s[0] == 'boards.4channel.org':
        chan = '4chan'
        s[3] = s[3].split('#')[0]
        api_url = 'https://a.4cdn.org/{}/thread/{}.json'.format(s[1], s[3])

    # 2ch
    elif s[0] == '2ch.hk':
        chan = '2ch'
        s[3] = s[3].split('.')[0]
        api_url = 'https://2ch.hk/makaba/mobile.fcgi?task=get_thread&board={}&thread={}&num={}'.format(s[1], s[3], s[3])

    # Dobrochan
    elif s[0] == 'dobrochan.ru':
        chan = 'dobrochan'
        s[3] = s[3].split('.')[0]
        api_url = 'http://dobrochan.ru/api/thread/{}/{}/all.json?new_format&message_html&board'.format(s[1], s[3])

    # Tumbach
    elif s[0] == 'tumba.ch':
        chan = 'tumbach'
        s[3] = s[3].split('.')[0]
        api_url = 'https://tumba.ch/{}/res/{}.json'.format(s[1], s[3])

    ### Wakaba based ###
    # Lolifox
    elif s[0] == 'lolifox.org':
        chan = 'lolifox'
        s[3] = s[3].split('.')[0]
        api_url = 'https://lolifox.org/{}/res/{}.json'.format(s[1], s[3])

    ### Anything else ###
    else:
        errexit('Unknown URL: {}'.format(raw_url))

    try:
        result = requests.get(api_url)
        if result.status_code != requests.codes.ok:
            result.raise_for_status()
    except requests.exceptions.RequestException as error:
        endfunc = errexit if not cliargs.skip_failed else print_c
        if result.status_code != 200:
            endfunc('Thread getting error. Code: {}'.format(result.status_code))
        else:
            endfunc('HTTPS connection error. Check connection and URL')
        return None, None, None

    re = result.json()
    u, f = parse_api(chan, s[1], re)
    return u, f, '{}-{}-{}'.format(chan, s[1], s[3])

def make_zip(path):
    zipname = path + '.zip'
    print_c('Creating {}...'.format(zipname))
    archive = zipfile.ZipFile(zipname, 'w')
    for root, _, files in os.walk(path):
        for f in files:
            print_verbose('  adding {}'.format(f))
            archive.write(
                os.path.join(root, f),
                compress_type = zipfile.ZIP_DEFLATED
            )
    if cliargs.verbose:
        print_c('Archive "{}" done!'.format(zipname))
    else:
        print_c('done!')

    if cliargs.only_zip:
        print_verbose('Removing directory "{}"...'.format(path))
        try:
            for root, dirs, files in os.walk(path):
                for f in files:
                    fpath = os.path.join(root, f)
                    print_verbose('  removing {}'.format(fpath))
                    os.remove(fpath)
                # Anyway...
                for d in dirs:
                    dpath = os.path.join(root, d)
                    print_verbose('  removing directory (?) "{}"'.format(dpath))
                    os.rmdir(dpath)
            os.rmdir(root)
        except OSError:
            errexit('OSError in file "{}"'.format(OSError.filename))
        print_verbose('"{}" has been removed!'.format(path))

def download_from_thread(http_url, thread_index, max_thread_index):
    media_urls, file_names, path = get_media_urls(http_url)
    if media_urls is None:
        return
    ulen = len(media_urls)

    start_index = int(cliargs.start_index) - 1 if cliargs.start_index else 0
    end_index = int(cliargs.end_index) if cliargs.end_index else ulen

    if start_index > ulen or end_index < 1:
        errexit('Indexes ({}-{}) is out of range ({})'.format(start_index, end_index, ulen))

    if output_directory != '':
        try:
            os.chdir(output_directory)
        except PermissionError:
            errexit('Cannot change directory "{}"'.format(output_directory))

    try:
        if os.path.exists(path):
            print_verbose('Directory "{}" already exists, skipping...'.format(path))
            pass
        else:
            print_verbose('Creating directory: ' + path)
            os.mkdir(path)
    except OSError:
        errexit('Cannot create a directory!')

    download_path = path + '/'
    for i in range(start_index, end_index):
        f = file_names[i].strip()
        u = media_urls[i]
        filepath = download_path + f
        journal_path = filepath
        if os.path.exists(filepath) and not cliargs.overwrite:
            print_verbose('"{}" already exists, skipping'.format(filepath), end='')
            continue
        else:
            outstr = '\b \r[{}/{}] {}   '.format(i + 1, ulen, f)
            print_c(outstr, end='')
            progress_sym()

        df = requests.get(u, verify=False)
        hasher = md5() if cliargs.md5 or cliargs.check else False

        with open(filepath, 'wb') as wf:
            for chunk in df.iter_content(2048):
                if hasher:
                    hasher.update(chunk)
                wf.write(chunk)

        journal_path = ''

        if cliargs.md5:
            hash = hasher.hexdigest()

            if cliargs.check:
                for file, sum in sum_list:
                    print_verbose('"{}" - "{}"'.format(file, sum))
                    if sum == hash:
                        print_verbose('Duplication: "{}" and "{}" ({})'.format(file, filepath, hash))
                        try:
                            os.remove(new_filepath)
                        except:
                            print_c('Cannot remove duplicated file: "{}"'.format(new_filepath))

            new_filepath = download_path + hash + '.' + filepath.split('.')[-1]
            try:
                os.rename(filepath, new_filepath)
            except FileExistsError:
                os.remove(filepath)

        global downloaded_files
        downloaded_files += 1

    print_c('\b\b\r"{}" done! ({} file(-s) downloaded)   '.format(path, downloaded_files))

    if cliargs.zip or cliargs.only_zip:
        make_zip(path)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, sigint_handler)
    global cliargs
    cliargs = init_parser()

    urllib3.disable_warnings()

    output_directory = cliargs.dir or ''

    urlsLen = len(cliargs.urls)
    for index, current in enumerate(cliargs.urls):
        print_c('\n[{}/{}] Requesting {}'.format(index + 1, urlsLen, current))
        download_from_thread(current, index, urlsLen)
