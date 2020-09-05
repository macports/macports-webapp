# Port Information

## Port List

Returns paginated and filterable port list.

**URL** : `/api/v1/ports/`

**Method** : `GET`

**Response example**

```json
{
    "count": 24161,
    "next": "http://127.0.0.1:8000/api/v1/ports/?page=2",
    "previous": null,
    "results": [
        {
            "name": "tex-whizzytex",
            "portdir": "tex/tex-whizzytex",
            "version": "1.3.6",
            "license": "GPL-2+",
            "platforms": "darwin",
            "epoch": 0,
            "replaced_by": null,
            "homepage": "http://cristal.inria.fr/whizzytex",
            "description": "An emacs minor mode for incremental viewing of LaTeX documents",
            "long_description": "An emacs minor mode for incremental viewing of LaTeX documents",
            "active": true,
            "categories": [
                "tex"
            ],
            "maintainers": [],
            "variants": [],
            "dependencies": [
                {
                    "type": "build",
                    "ports": [
                        "clang-9.0"
                    ]
                },
                {
                    "type": "lib",
                    "ports": [
                        "texlive"
                    ]
                }
            ],
            "depends_on": []
        },
        ...
    ]
}
```
**Parameters**

- `name` : Filter the list by port name
- `categories`: Display ports belonging to this category
- `maintainers_github`: Display ports belonging to this github handle
- `variants_variant`: Display ports with this variant

## Port Detail

Returns complete information for a port

**URL** : `/api/v1/ports/{port-name}`

**Method** : `GET`

**Response example**

```json
{
    "name": "mpstats",
    "portdir": "sysutils/mpstats",
    "version": "0.1.8",
    "license": "BSD",
    "platforms": "darwin",
    "epoch": 0,
    "replaced_by": null,
    "homepage": "https://www.macports.org/",
    "description": "submit statistics about your macports installation",
    "long_description": "This is a script and LaunchAgent which will run weekly to report information about your system and installed ports to a server, which publishes the aggregate statistics on the web. \nThis helps us to make better decisions on which configurations we should support and test more and which ports are most commonly used.",
    "active": true,
    "categories": [
        "sysutils",
        "macports"
    ],
    "maintainers": [
        {
            "name": "cal",
            "github": "neverpanic",
            "ports_count": 182
        }
    ],
    "variants": [],
    "dependencies": [
        {
            "type": "build",
            "ports": [
                "clang-9.0"
            ]
        }
    ],
    "depends_on": []
}
```