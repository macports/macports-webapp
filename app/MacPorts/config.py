import os
from MacPorts.settings import BASE_DIR

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

# configuration for repository to find updated ports
MACPORTS_PORTS = "macports-ports"
MACPORTS_PORTS_DIR = os.path.join(DATA_DIR, "macports-ports")
MACPORTS_PORTS_URL = "https://github.com/macports/macports-ports.git"

# configuration for fetching builders
BUILDERS_JSON_URL = "https://build.macports.org/json/builders/"

# configuration for tests
TEST_SAMPLE_DATA = os.path.join(BASE_DIR, 'ports', 'tests', 'sample_data')
TEST_PORTINDEX_JSON = os.path.join(TEST_SAMPLE_DATA, 'portindex.json')
PORTINDEX2JSON = os.path.join(TEST_SAMPLE_DATA, 'macports-contrib', 'portindex2json', 'portindex2json.tcl')
