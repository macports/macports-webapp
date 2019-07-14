import os

# configuration for rsync
RSYNC = '/usr/bin/rsync'
RSYNC_SOURCE = "rsync://rsync.macports.org/macports//trunk/dports/PortIndex_darwin_18_i386/PortIndex.json"
JSON_FILE = os.path.join(os.path.abspath(os.path.dirname(__name__)), 'portindex.json')

# configuration for repository to find updated ports
REPO = "macports-ports"
REPO_URL = "https://github.com/macports/macports-ports.git"
