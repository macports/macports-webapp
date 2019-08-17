## 4. Supplying Initial Data

The following models are supplied with initial data:

*All models related to PortIndex*
- [Port](/docs/3-MODELS.md#1-the-port-model)
- [Category](/docs/3-MODELS.md#2-the-category-model)
- [Maintainer](/docs/3-MODELS.md#3-the-maintainer-model)
- [Dependency](/docs/3-MODELS.md#5-the-dependency-model)
- [Variant](/docs/3-MODELS.md#4-the-variant-model)
- [LastPortIndexUpdate](/docs/3-MODELS.md#6-the-lastportindexupdate-model)

*Active builders*
- [Builder](/docs/3-MODELS.md#1-the-builder-model)

#### Auto-loading the Intial Data

The process to load initial data is handled by a [custom Django-admin command](/app/ports/management/commands/autoload-initial-data.py): 

```
python manage.py autoload-inital-data
```

The command can only be run be if the `Port` and `Builder` tables both are empty.

Data for the tables related to PortIndex comes from the file `portindex.json`. This file is a JSON version of the `PortIndex`
converted using the script [portindex2json.tcl](https://github.com/macports/macports-contrib/tree/master/portindex2json).
The file is generated regularly by [mprsyncup](https://github.com/macports/macports-infrastructure/blob/master/jobs/mprsyncup)
job and distributed through rsync. Structure of the `portindex.json` file is shown below:

```json
{
    "info": {
        "commit": "GIT SHASUM OF THE LATEST COMMIT AT THE TIME OF GENERATING THE FILE."
    },
    "ports": [
        {
            "name": "AppHack",
            "version": "1.1",
            "...more fields...": "..."
        }, 
        {
            "name": "wget",
            "version": "1.20.3",
            "...more fields...": "..."
        }
    ]
}
```

The file is first fetched from the rsync server using a method of the Port Model: [`Port.PortIndexUpdateHandler()`](/app/ports/models/port.py#L286).
It first fetches the latest file from the rsync server, the address of which is defined in `Macports.config.PORTINDEX_SOURCE`.
The file is stored in the [data](/app/data) directory.
The method returns the entire JSON object from the file.

The object ports is then supplied to the method [`Port.load()`](/app/ports/models/port.py#L38), the actual populating of the tables now starts.

- The `load_categories_table` method first loads the `Category` model in a single query using `bulk_create`.
- Next, the `Port`, `Maintainer` and `Variant` tables are populated in a single transaction.
    - While looping over the JSON ojects containing information of a single port, if any of the following keys is missing,
    the port is not added to the database: `name`, `portdir`, `version`.
    - The unique triplet for the `Maintainer` model is taken care of. If any of the `name`, `domain` or `github` fields is
    missing, then default `''` is used.
    - Relation to the `Category` table is defined using the `object.categories.add()` method.
    - `Variant` table is also populated.
    - A `port_id_map` dictionary is generated which contains the `id` and `name` of the port corresponding to the `primary key`
    and `name` fields from the `Port` model. This helps to populate the `Dependency` table without querying the database each time
    to get the `primary key` of the related port.
- The third and final step of the `Port.load()` method is to populate the `Dependency` table. This happens in another
single transaction.
    - For each port, the various types of dependencies go into separate rows.
    - The `port_id_map` dictionary helps to add relations (one-to-one and many-to-many) by making available the `primary key`
    of any object from the `Port` table immediately without having to query the database.
    - The internal method `load_depends` takes in the `port`, `type of dependency` and `list of dependencies` arguments
    populates the database. For each port we now have the type of dependency and all the related ports (dependencies).
    
When the above tasks finish successfully, the command moves on to populate the `Builder` table. For which it uses the JSON
api from buildbot, the URL to which is defined in the `config` file: `BUILDERS_JSON_URL`.

A method of the `BuildHistory` model, [`BuildHistory.populate_builder`](/app/ports/models/buildhistory.py#L110) populates
the builders table.

The initial data loading process then finishes.

---

#### Loading the initial data by manually supplying PortIndex.json

The method `Port.load()` can also accept path to a `PortIndex.json` file and then perform the data loading process as
discussed above.

When the method `Port.load()` receives a path (string), it tries to open the path and then load the database. There is also
a custom dajngo-admin command written in the app for this:

```
python manage.py load <path-to-portindex-json>
```

**NOTE**: This method of loading initial data will not load the `Builder` table.