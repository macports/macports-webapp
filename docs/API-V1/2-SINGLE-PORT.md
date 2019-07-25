## Details of a Single Port

#### `- GET /port/`

Fetch the general information about a port i.e. the data extracted from the `Portfile`.

Parameters:

| key | type | details | default |
|------|-----|----|----|
| name | str, required | Name of the port | -- |
| field | str, optional | Select only a particular field. If not provided, then all fields are sent.| All |

#### - `GET /port/builds/`

Fetch build history of a given port.

Parameters

| key | type | details | default |
|------|-----|----|----|
| name | str, required | Name of the Port | -- |
| count | int, optional | Number of builds to be fetched for each builder. | All |
| builder | str, optional | Specify one more builders, separated by comma (`,`). | All |
| status | str, optional | Filter by the status of builds. | All |


#### - `GET /port/stats/`

Fetch installation statistics of a given port.

Parameters

| key | type | details | default
|------|-----|----|----|
| name | str, required | Name of the Port | -- |
| days_ago | int, optional | Number of days behind current day, to calculate stats. | 0 |
| days | int, optional | Number of days behind `days_ago`. Only the submissions made in this period are used to generate the stats. | 30 |
| criteria | optional | Comma separated list of the criterial of stats. Options: ['total_count', 'req_count', 'os', 'xcode', 'os_arch', 'cxx_stdlib'] | All |
    
- ***total_count***: The total number of users having the port installed.
- ***req_count***: The number of users who requested the port.
- ***os***: Distribution of total users across various OSX versions.
- ***xcode***: Distribution of total users across various OSX versions.
- ***os_arch***: Distribution of total users across various OS architectures.
