## Details of a Single Port

#### `- GET /port/{port-name}/info`

Fetch the general information about a port i.e. the data extracted from the `Portfile`.

Parameters:

| key | type | details | default |
|------|-----|----|----|
| field | str, optional | Select only a particular field. If not provided, then all fields are sent.| All |

#### - `GET /port/{port-name}/builds`

Fetch build history of a given port.

Parameters

| key | type | details | default |
|------|-----|----|----|
| count | int, optional | Number of builds to be fetched for each builder. | All |
| builder | str, optional | Specify one or more builders, separated by comma (`,`). | All |
| status | str, optional | Filter by the status of builds. | All |


#### - `GET /port/{port-name}/stats`

Fetch installation statistics of a given port.

Parameters

| key | type | details | default
|------|-----|----|----|
| days_ago | int, optional | Number of days behind current day, to calculate stats. | 0 |
| days | int, optional | Number of days behind `days_ago`. Only the submissions made in this period are used to generate the stats. | 30 |
| criteria | optional | Comma separated list of the criteria of stats. Options: ['total_count', 'req_count', 'os', 'xcode'] | All |
    
- ***total_count***: The total number of users having the port installed.
- ***req_count***: The number of users who requested the port.
- ***os***: Distribution of total users across various combinations of OSX versions, build architecture and stdlib.
- ***xcode***: Distribution of total users across various combinations OSX and XCode versions.

#### - `GET /port/{port-name}/health`

Returns the status of latest build of the port on each builder

Parameters

| key | type | details | default
|------|-----|----|----|
| builders | str, optional | Comma separated list of builders | All |

```json
    [
        {
            "builder1": "build successful",
            "builder2": "failed install-port",
        }
    ]
```
