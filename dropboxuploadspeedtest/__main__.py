#!/usr/bin/env python3

import configparser
import os
import signal
import sys
import time

import dropbox

def main():
    config_dir = os.path.join(
        os.environ.get('XDG_CONFIG_HOME') or os.path.join(os.path.expanduser('~'), '.config'),
        'dropboxuploadspeedtest')
    config_filename = os.path.join(config_dir, 'config.ini')

    config = configparser.ConfigParser()
    if len(config.read(config_filename)) == 0:
        raise Exception("Configuration file couldn't be read: %s" % config_filename)

    dbx = dropbox.Dropbox(config['default']['access token'])

    chunk_size = int(float(sys.argv[1]) * 2 ** 20)
    chunk = bytearray(os.urandom(chunk_size))
    print("Finished creating random data chunk of %d bytes" % chunk_size)

    exit = False
    def sigint_handler(signal, frame):
        print("Exiting after next chunk completion")
        nonlocal exit
        exit = True
    for s in (signal.SIGINT, signal.SIGTERM):
        signal.signal(s, sigint_handler)

    cursor = dropbox.files.UploadSessionCursor(dbx.files_upload_session_start(b'').session_id, 0)
    start_time = time.time()
    while not exit:
        chunk_start_time = time.time()
        dbx.files_upload_session_append_v2(chunk, cursor)
        cursor.offset += chunk_size

        now = time.time()
        chunk_speed_kibps = (chunk_size / (now - chunk_start_time)) / 1024
        total_speed_kibps = (cursor.offset / (now - start_time)) / 1024
        print("Last chunk: %d KiB/s\tOverall: %d KiB/s" % (chunk_speed_kibps, total_speed_kibps))

    print("Deleting test file")
    path = '/dropboxuploadspeedtest.bin'
    dbx.files_upload_session_finish(b'', cursor,
        dropbox.files.CommitInfo(path, dropbox.files.WriteMode.overwrite))
    dbx.files_delete(path)
