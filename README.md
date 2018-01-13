# simple-transmission-rss
Bare-bones cron-friendly rss torrent handler for transmission

Requires python2.7, transmissionrpc (https://pypi.python.org/pypi/transmissionrpc/), and feedparser (https://github.com/kurtmckee/feedparser)

I threw this together because I encountered issues with an alternative and decided that it would probably faster to roll my own than to grok the alternative (and because there exist python modules to do the uninteresting bits).

The goal was to have a simple, understandable and correct script, easy to configure and invokable from cron, to add torrents from RSS feeds to my transmission daemon. A consequence of this simplicity is hackability: I don't expect this to be a one-size-fits-all solution and didn't attempt to design in much configurability/flexibility. Instead, the design is intended to empower modifications to fit individual use cases. Furthermore, this (obviously) wasn't intended as Enterprise™ Grade™ Python™ and I have no interest in making it so.

Configuration is fairly obvious: global settings captures daemon connection info. Leave values as `None` if unneeded. The `FEEDS` list contains dicts, each dict representing a particular feed's configuration. Named keys (`pattern dl_dir subdirs subdir_pattern subdir_match_index url`) are expected. If `subdirs` is `True`, subdirectories named match group index `subdir_match_index` of `subdir_pattern` matched against the torrent title (from the feed, *not* the actual title of the torrent) are created if needed and used as the download directory within the overall download directory. If `False`, torrents are downloaded directly into `dl_dir`. 

If you're sane, you'll be using a virtualenv. To make cron happy, invoke the script with the python binary from your virtualenv, avoiding shell expansion.
For example, invoking on the hour every hour,
```
0 * * * * /usr/home/orc/trss/bin/python2.7 /usr/home/orc/trss/trss.py
```
Depending on your preferred log location, you may need to `touch` and `chmod/chown` the file beforehand. I considered `syslog` integration, but that's a pain and not as portable as it should be. 

# Example configuration
```
LOG = '/var/log/trss.log'
LOGLEVEL = logging.INFO
HOST = 'localhost'
PORT = 9091
USER = None
PASSWORD = None
HTTP_HANDLER = None
TIMEOUT = None

FEEDS = [
{
'pattern' : '.*(some real name|another real name).*placebo resolution.*some subgroup.*Episode.*',
'dl_dir' : '/a/',
'subdirs' : True,
'subdir_pattern' : '(.*) ::',
'subdir_match_index' : 1,
'url' : 'https://[redacted sekrit club :^)]'
},
{
'pattern' : '.*(some real name|another real name).*Episode.*',
'dl_dir' : '/tv/',
'subdirs' : True,
'subdir_pattern' : '(.*) ::',
'subdir_match_index' : 1,
'url' : 'https://[redacted sekrit club :^)]'
}
]
```
