import json
import re
import os
import logging
import feedparser
import transmissionrpc


LOG_LEVELS = {
    'NOTSET': logging.NOTSET,
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

CONFIG_FILE = file(os.path.join(os.path.dirname(__file__), 'config.json'))
CONFIG = json.load(CONFIG_FILE)

# Feed configuration: each feed is a dict with expected keys
FEEDS = CONFIG['feeds']

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVELS.get(CONFIG['logging'].get('level', 'INFO'), logging.INFO))
handler = logging.FileHandler(CONFIG['logging'].get('file', '/var/log/trss.log'))
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def process_feed(url, pattern, dl_dir, subdirs, subdir_pattern, subdir_match_index, tc):
    try:
        feed = feedparser.parse(url)
    except Exception:
        logger.error('Failed to fetch feed for feed %s', url, exc_info=True)
    try:
        r = re.compile(pattern)
    except Exception:
        logger.error('Failed to compile regular expression %s for feed %s', pattern, url, exc_info=True)
    entries = [e for e in feed.entries if r.match(e.title)]
    logger.debug('Fetched %d matching entries', len(entries))
    for e in entries:
        if subdirs:
            try:
                p = re.compile(subdir_pattern)
            except Exception:
                logger.error('Failed to compile regular expression %s for feed %s', pattern, url, exc_info=True)
            m = p.match(e.title)
            path = dl_dir + m.group(subdir_match_index)
        else:
            path = dl_dir
        if not os.path.isdir(path):
            try:
                os.makedirs(path)
            except Exception:
                logger.error('Failed to create working directory %s for feed %s', path, url, exc_info=True)
        tc.add_torrent(e.link, download_dir=path)
        logger.info('Added torrent %s at path %s', e.title, path)


try:
    client = transmissionrpc.Client(**CONFIG['transmission'])
except Exception:
    logger.error('Failed to connect to daemon', exc_info=True)

for feed in FEEDS:
    logger.info('Processing feed %s', feed['url'])
    feed.update({'tc' : client})
    process_feed(**feed)
