## Installation Statistics

#### `- GET /stats/general`

Fetch general stats like the number of total submissions and the number of unique users

Parameters:

| key | type | details | default |
|------|-----|----|----|
| days | int, optional | Previous X days for which the counting is done | 30 |
| days_ago | int, optional | Goes back in time by Y days and then starts the counting for previous X days provided by the key 'days' | 0 |
| all_time | bool,  optional | Adds an object to return stats since the very beginning | False |

```json
{
    "all_time": {
        "total_submissions": 200,
        "total_users": 67,
        "users_last_7_days": 32,
        "users_last_30_days": 48
    },
    "in_duration": {
        "total_submissions": 45,
        "total_users": 7
    }
}
```

#### `- GET /stats/system`

Fetch system stats like os_version, xcode version, MacPorts version etc.

Parameters:

| key | type | details | default
|------|-----|----|----|
| days | int, optional | Previous X days for which the counting is done | 30 |
| days_ago | int, optional | Goes back in time by Y days and then starts the counting for previous X days provided by the key 'days' | 0 |
| criteria | optional | Comma separated list of the criteria of stats. Options: ['os_stats', 'xcode_stats', 'macports_stats'] | All |
    
- ***os***: Distribution of total users across various combinations of OSX versions, build architecture and stdlib.
- ***xcode***: Distribution of total users across various combinations OSX and XCode versions.
- ***macports***: Distribution of total users across various MacPorts versions.

```json
{
    "os_stats": [{
        "os_version": "10.14",
        "build_arch": "x86_64",
        "cxx_stdlib": "libc++",
        "count": 45
    }, {
        "os_version": "10.13",
        "build_arch": "x86_64",
        "cxx_stdlib": "libc++",
        "count": 25
    }],
    
    "xcode_stats": [{
        "os_version": "10.14",
        "xcode_version": "10.2.1",
        "count": 25
    }]
}
```

#### `- GET /stats/top-ports`

Fetch the list of ports with highest number of installations.

Parameters:

| key | type | details | default |
|------|-----|----|----|
| count | int, optional | The number of top ports to be returned | 100 |
| sort_by_1 | str, optional | First priority of sorting | '-total_count' |
| sort_by_2 | str, optional | Second priority of sorting | '-requested_count' |
| sort_by_3 | str, optional | Third priority of sorting | 'port-name' |
| port_filter | str, optional | 'icontains' matching with port-names using the provided string | All |
| days | int, optional | Previous X days for which the counting is done | 30 |
| days_ago | int, optional | Goes back in time by Y days and then starts the counting for previous X days provided by the key 'days' | 0 |

```json
[
    {
        "port": "wget",
        "total_count": 11,
        "requested_count": 13
    },
    {
        "port": "ImageMagick",
        "total_count": 12,
        "requested_count": 6
    }
]
```
