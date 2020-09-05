# MacPorts Webapp API v1

The v1 of the API only supports `GET` requests because the primary purpose of this version is to only allow fetching of
data and not manipulation. All the endpoints are open and do not require authentication.

## Open Endpoints

### Port information
* [Ports list](#) : `GET /api/v1/ports/`
* [Port detail](#) : `GET /api/v1/ports/{port-name}/`

### Categories
* [Categories list](#) : `GET /api/v1/category/`
* [Category detail](#) : `GET /api/v1/category/{category-name}/`

### Maintainers
* [Maintainers list](#) : `GET /api/v1/maintainers/`
* [Port detail](#) : `GET /api/v1/maintainers/{maintainer-github}/`

### Build History
* [All builds](#) : `GET /api/v1/builds/`
* [Build detail](#) : `GET /api/v1/builds/{pk}/`
* [Builders list](#) : `GET /api/v1/builders/`
* [Files](#) : `GET /api/v1/files/{build-pk}/`

### Search (from Solr)
* [Search](#) : `GET /api/v1/search/`
* [Port name autocomplete](#) : `GET /api/v1/autocomplete/port/`
* [Category autocomplete](#) : `GET /api/v1/autocomplete/category/`
* [Maintainer autocomplete](#) : `GET /api/v1/autocomplete/maintainer/`
* [Variant autocomplete](#) : `GET /api/v1/autocomplete/variant/`
