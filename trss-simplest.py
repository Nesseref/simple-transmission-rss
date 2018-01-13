#!/usr/local/bin/python2.7

import transmissionrpc
import feedparser
import re
import os

PATTERN = ''
DL_DIR = ''
SUBDIRS = True
URL = ''
HOST = ''

tc = transmissionrpc.Client(HOST)
feed = feedparser.parse(URL)
r = re.compile(PATTERN)
entries = [e for e in feed.entries if r.match(e.title)]
p = re.compile('(.*)::')
for e in entries:
    m = p.match(e.title)
    if SUBDIRS:
        path = DL_DIR + m.group(1)[:-1]
    else:
        path = DL_DIR
    if not os.path.isdir(path):
        os.makedirs(path)
    tc.add_torrent(e.link, download_dir=path)
