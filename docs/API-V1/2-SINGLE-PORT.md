## Details of a Single Port

#### - GET /port/

Fetch the general information about a port i.e. the data extracted from the `Portfile`.

Params:
- **name** [required]: Name of the port
- **field** [optional]: Select only a particular field. If not provided, then all fields are sent. [default: All]

#### - GET /port/builds/

Fetch build history of a given port.

Params
- **name** [required]: Name of the Port
- **count** [optional]: Number of builds to be fetched for each builder. [default: All]
- **builder** [optional]: Specify one more builders, separated by comma (`,`). [default: All]
- **status** [optional]: Filter by the status of builds. [default: All]


#### - GET /port/stats/

Re

Params
- **name** [required]: Name of the Port
- **days_ago** [optional, integer]: Number of days behind current day, to calculate stats. [default: 0]
- **days** [optional, integer]: Number of days behind `days_ago`. Only the submissions made in this period are used to 
    generate the stats. [default: 30]
- **criteria** [optional]: Comma separated list of the criterial of stats. Options: ['total_count', 'req_count', 'os', 'xcode', 'os_arch', 'cxx_stdlib'] [default: All]
    - *total_count*: The total number of users having the port installed.
    - *req_count*: The number of users who requested the port.
    - *os*: Distribution of total users across various OSX versions.
    - *xcode*: Distribution of total users across various OSX versions.
    - *os_arch*: Distribution of total users across various OS architectures.
