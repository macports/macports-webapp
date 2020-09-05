## 2. SOURCES (Collection of Data)

Before going into the technicalities of the project, it is important to understand where the app gets the data from, 
which is later processed and displayed.

Currently, there are four sources of information for the app:

#### 1. Port Information

All the information that is needed is contained in the port's `Portfile`. The `portindex` command generates a file
containing information about each port in the form of TCL arrays.

Another TCL script, [portindex2json.tcl](https://github.com/macports/macports-contrib/blob/master/portindex2json/portindex2json.tcl)
converts the TCL arrays into JSON objects. The app has support for directly accepting these JSON objects to add or update
information about the ports. `PortIndex.json` is also generated and distributed through rsync by the job [mprsyncup](https://github.com/macports/macports-infrastructure/blob/master/jobs/mprsyncup).

Keeping the port information updated is discusses in `UPDATES` section.

#### 2. Build Information

The [buildbot](https://build.macports.org) is where all the builds take place. Its JSON API makes available the info
about last 10,000 builds. The app fetches these and from buildbot and stores them in its own database.

#### 3. Installation Statistics

Users have to install the port [mpstats](https://github.com/macports/macports-ports/tree/master/sysutils/mpstats) in
order to be able to submit the information about the installed ports and details about their system (OS, MacPorts version,
Xcode version). The port automatically submits a JSON object to the app weekly, and the submission can be triggered
manually by the user as well. Each user is represented by a unique `UUID` and the information is saved in the database
along with a timestamp, it is then processed to display statistics.

#### 4. Trac

Tickets related to each port are scraped from [trac.macports.org](https://trac.macports.org)