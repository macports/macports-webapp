import os
from settings import BASE_DIR

# data directory
# the data required by app- portindex.json, macports-ports repository etc. live here
DATA_DIR = os.path.join(BASE_DIR, "data")

# commands
GIT = "/usr/bin/git"
TCLSH = "/usr/bin/tclsh"

# configuration for rsync
RSYNC = "/usr/bin/rsync"
PORTINDEX_SOURCE = "rsync://rsync.macports.org/macports//trunk/dports/PortIndex_darwin_18_i386/PortIndex.json"
PORTINDEX_JSON = os.path.join(DATA_DIR, "portindex.json")

# configuration required for macports repositories
MACPORTS_PORTS = "macports-ports"
MACPORTS_CONTRIB = "macports-contrib"
MACPORTS_PORTS_DIR = os.path.join(DATA_DIR, MACPORTS_PORTS)
MACPORTS_CONTRIB_DIR = os.path.join(DATA_DIR, MACPORTS_CONTRIB)
MACPORTS_PORTS_URL = "https://github.com/macports/macports-ports.git"
MACPORTS_CONTRIB_URL = "https://github.com/macports/macports-contrib"

# configuration for locally generated portindex.json
LOCAL_PORTINDEX = os.path.join(MACPORTS_PORTS_DIR, 'PortIndex')
LOCAL_PORTINDEX_JSON = os.path.join(MACPORTS_PORTS_DIR, 'portindex.json')
PORTINDEX2JSON = os.path.join(MACPORTS_CONTRIB_DIR, 'portindex2json', 'portindex2json.tcl')

# configuration for fetching builders
BUILDERS_JSON_URL = "https://build.macports.org/json/builders/"

# configuration for fetching builds
BUILDBOT_URL_PREFIX = "https://build.macports.org"
BUILDS_FETCHED_COUNT = 5

# configuration for tests
TEST_SAMPLE_DATA = os.path.join(BASE_DIR, 'tests', 'sample_data')
TEST_PORTINDEX_JSON = os.path.join(TEST_SAMPLE_DATA, 'portindex.json')

# port command
PORT_COMMAND = "/opt/local/bin/port"
