import transmissionrpc
import feedparser
import re
import os
import logging

'''
Global settings
'''
LOG = '/var/log/trss.log'
LOGLEVEL = logging.INFO
HOST = 'localhost'
PORT = 9091
USER = None
PASSWORD = None
HTTP_HANDLER = None
TIMEOUT = None 

'''
Feed configuration: each feed is a dict with expected keys
'''
FEEDS = [
{
'pattern' : '',
'dl_dir' : '',
'subdirs' : True,
'url' : ''
}
]

logger = logging.getLogger(__name__)
logger.setLevel(LOGLEVEL)
handler = logging.FileHandler(LOG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def process_feed(url, pattern, dl_dir, subdirs, tc):
    try:
        feed = feedparser.parse(url)
    except Exception, e:
        logger.error('Failed to fetch stream', exc_info=True)
    r = re.compile(pattern)
    entries = [e for e in feed.entries if r.match(e.title)]
    logger.debug('Fetched %d matching entries', len(entries))
    p = re.compile('(.*)::')
    for e in entries:
        m = p.match(e.title)
        if subdirs:
            path = dl_dir + m.group(1)[:-1]
        else:
            path = dl_dir
        if not os.path.isdir(path):
            os.makedirs(path)
        tc.add_torrent(e.link, download_dir=path)
        logger.info('Added torrent %s at path %s', e.title, path)

try:
    client = transmissionrpc.Client(HOST, PORT, USER, PASSWORD, HTTP_HANDLER, TIMEOUT)
except Exception, e:
    logger.error('Failed to connect to daemon', exc_info=True)

for feed in FEEDS:
    logger.info('Processing feed %s', feed['url'])
    process_feed(feed['url'], feed['pattern'], feed['dl_dir'], feed['subdirs'], client)


