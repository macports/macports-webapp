import os
from MacPorts.settings import BASE_DIR

# data directory
# the data required by app- portindex.json, macports-ports repository etc. live here
DATA_DIR = os.path.join(BASE_DIR, "data")

# git
GIT = "/usr/bin/git"

# configuration for rsync
RSYNC = "/usr/bin/rsync"
PORTINDEX_SOURCE = "rsync://rsync.macports.org/macports//trunk/dports/PortIndex_darwin_18_i386/PortIndex.json"
PORTINDEX_JSON = os.path.join(DATA_DIR, "portindex.json")

# configuration for repository to find updated ports
MACPORTS_PORTS = "macports-ports"
MACPORTS_PORTS_DIR = os.path.join(DATA_DIR, "macports-ports")
MACPORTS_PORTS_URL = "https://github.com/macports/macports-ports.git"
