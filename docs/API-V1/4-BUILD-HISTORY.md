## Build History

#### `- GET /builds/`

Fetch all builds or only few latest builds.

Parameters:

| key | type | details | default |
|------|-----|----|----|
| count | int, optional | The number of latest builds to be fetched for each builder | All |
| paginate_by | int, optional | Number of objects on each page | 100 |
| page | int, optional | Page to be loaded | 1 |
| builder | str, optional | Comma separated list of builders for which the builds are to be fetched | All |
| status | str, optional | Comma separated list of status, only corresponding builds are sent | All |
| status_code | int, optional | Comma separated list of status codes, only corresponding builds are sent | All |
| ports | str, optional | Comma separated list of port-names for which builds are to be fetched | All |
| time | datetime, optional | The time since which builds are to be fetched | All |
