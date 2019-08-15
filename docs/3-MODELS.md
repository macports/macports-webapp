## 2. MODELS (Storing the collected data)

The data collected from various sources, as discussed in [2-SOURCES](/docs/2-SOURCES.md), is stored in a PostgreSQL
database. The tables are designed using Django models.

All of the project's models are defined inside the app: `ports`. The models are split into three different files: `port`,
`buildhistory` and `stats`. Each file contains the models related to the category defined by file name.

#### 1. `Port` Model

It stored the basic information related to a port, with the following fields:
- `portdir`
- `description`
- `homepage`
- `epoch`
- `platforms`
- `categories` - A many-to-many relation with `Category` model
- `long_description`
- `version`
- `revision`
- `closedmaintainer`
- `name`
- `license`
- `replaced_by` - Default values is `Null` for active ports. If the value is not null, the port is considered as obsolete.
- `active` - Value is `False` for deleted ports, otherwise `True`*.

***A Port is marked as deleted when the port is available in the app's database, but does not exist in PortIndex. If a 
port with the same name is added later in time, then previous object is replaced with new object and the newer ports gets
marked as `active=True` automatically.*

#### 2. `Category` Model

Contains the categories in which the ports is divided. It is related with the `Port` model using a many-to-many relation.
The model has a single field `name` which also becomes the primary key for the table.

#### 3. `Maintainer` Model

Stores email and github-handle of the maintainers, and maps them with objects from the `Port` model.

- `name`
- `domain`
- `github`
- `ports`- many-to-many relation with the `Port` Model.

*The `name`, `domain`, `github` triplet is unique. But due to inconsistencies in the `Portfiles`, there might be cases
when we have two entries with same github-handle but different emails. In such cases, a warning is displayed on the
maintainer's page.*

#### 4. `Variant` Model

Stores the variant and maps it to the related objects from the `Port` Model. It has only two fields:
- `port` - foreign key to `Port` Model
- `variant`


#### 5. `Dependency` Model

Contains relation for ports and their dependencies:

- `port_name` - foreign key to `Port` model
- `dependencies` - many-to-many relation with `Port` model
- `type`


#### 6. `LastPortIndexUpdate` Model

Stores only one object. The object tells about the git commit till which the port information is up-to-date and the time
when the update was carried out.

- `git_commit_hash`
- `updated_at`

---

#### 7. `Builder` Model

Stores names of the active builders from Buildbot. The build history is fetched only for these builders. This is the only
place where information about builders is stored.

#### 8. `BuildHistory` Model

The JSON received from buildbot is stored in this Model. Details of one build is one object for this model.

- `builder_name` - foreign key to `Builder` Model
- `build_id`
- `status`
- `port_name`
- `time_start`
- `time_elapsed`
- `watcher_id`

---

#### 9. `UUID` Model

Stores UUID of the users who have made submissions. There are no duplicates in the table, no matter how many submissions
one user makes there is only one object representing the user.

#### 10. `Submission` Model

The body of the submission made by the user is stored in this model, except the installed ports which have their own
model.

- `user` - foreign key to `UUID` model
- `os_version`
- `xcode_version`
- `os_arch`
- `build_arch`
- `platform`
- `macports_version`
- `cxx_stdlib`
- `clt_version`
- `raw_json` - stores the entire JSON object received in the submission
- `timestamp`

#### 11. `PortInstallation` Model

Stores the installed ports received from a particular submission with their versions and variants.

- `submission` - foreign key to `Submission` model
- `port`
- `version`
- `variants`
- `requested` - (bool) whether the port was requested or not.
