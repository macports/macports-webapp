## Filter Ports

#### `- GET /ports/`

Returns the list of port-names or full port objects (if `info=True`) matching the specified criteria.

Parameters:

| key | type | details | default |
|------|-----|----|----|
| icontains | str, optional | Case insensitive matching by port-name | All |
| contains | str, optional | Case sensitive matching by port-name | All |
| category | str, optional | Filter ports by category | All |
| description | str, optional | Search by description | All |
| variant | str, optional | Filter by variant | All |
| maintainer_github | str, optional | Filter by maintainer's github handle | All |
| maintainer_email | str, optional | Filter by maintainer's email | All |
| info | Boolean, optional | Entire object is returned and not just the port-name | False |
| keys | str, optional | Comma separated list of keys which should be returned and not just port-name | Nil |
