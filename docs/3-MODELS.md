## 2. MODELS (Storing the collected data)

- [PortIndex](#portindex)
    - [Port](#1-the-port-model)
    - [Category](#2-the-category-model)
    - [Maintainer](#3-the-maintainer-model)
    - [Variant](#4-the-variant-model)
    - [Dependency](#5-the-dependency-model)
    - [LastPortIndexUpdate](#6-the-lastportindexupdate-model)
- [Build History](#build-history)
    - [Builder](#1-the-builder-model)
    - [BuildHistory](#2-the-buildhistory-model)
- [Installation Statistics](#installation-statistics)
    - [UUID](#1-the-uuid-model)
    - [Submission](#2-the-submission-model)
    - [PortInstallation](#3-the-portinstallation-model)

---

The data collected from various sources, as discussed in [2-SOURCES](/docs/2-SOURCES.md), is stored in a PostgreSQL
database. The tables are designed using Django models.

All of the project's models are defined inside the app: `ports`. The models are split into three different files: [port](/app/ports/models/port.py),
[buildhistory](/app/ports/models/buildhistory.py) and [stats](/app/ports/models/stats.py). Each file contains the models
related to the category defined by file name.

### PortIndex

#### 1. The Port Model

Column | Type | Notes
-------|------|-------
name | character field | unique, max-length = 100
portdir | character field | max-length=100
description | text field | default = ''
homepage | url field | default = ''
epoch | big integer field | default = 0
platforms | text field | default = Null
categories | many-to-many field | related to the Category model
long_description | text field | default = ''
version | character field | default = ''
revision | integer field | default = 0
closedmaintainer | boolean field | default = False
license | character field | default = '', max-length = 100
replaced_by | character field | nullable, max-length = 100
active | boolean field | default = True

- **replaced_by**: `NULL` by default. If the port is obsolete and replaced by another one, the name of the new port is 
stored here.
- **active**: `True` by default. `False` when the port no longer exists (in `PortIndex`).

#### 2. The Category Model

Column | Type | Notes
-------|------|------
name | text field | primary-key

#### 3. The Maintainer Model

Column | Type | Notes
-------|------|------
name | char field | default = '', max-length = 50
domain | char field | default = '', max-length = 50
github | char field | default = '', max-length = 50
ports | many-to-many field | related to the Port model

- The `name`, `domain`, `github` triplet is unique. But due to inconsistencies in the `Portfiles`, there might be cases
when we have two entries with same github-handle but different emails. In such cases, a warning is displayed on the
maintainer's page.

- Example of inconsistency: https://ports.macports.org/maintainer/github/yan12125/

#### 4. The Variant Model

Column | Type | Notes
-------|------|------
port | foreign key | related to the Port model
variant | character field | default = '', max-length = 100

#### 5. The Dependency Model

Column | Type | Notes
-------|------|------
port_name | foreign key | related to the Port model
dependencies | many-to-many field | related to the Port model
type | character field | max-length = 100


#### 6. The LastPortIndexUpdate Model

Column | Type | Notes
-------|------|------
git_commit_hash | character field | max-length = 50
updated_at | datetime field | auto_now = True

- Stores only one object. The object tells about the git commit till which the port information is up-to-date and the time
when the update was carried out.

---

### Build History

#### 1. The Builder Model

Column | Type | Notes
-------|------|------
name | character field | unique, max-length = 100

- Stores names of the active builders from Buildbot. The build history is fetched only for these builders. This is the only
place where information about builders is stored.

#### 2. The BuildHistory Model

Column | Type | Notes
-------|------|------
builder_name | foreign key | related to the Builder model
build_id | integer field |
status | character field | max-length = 50
port_name | character field | max-length = 100
time_start | datetime field |
time_elapsed | time field | nullable
watcher_id | integer field |

- The JSON received from buildbot is stored in this Model. Details of one build is one object for this model.

---

### Installation Statistics

#### 1. The UUID Model

Column | Type | Notes
-------|------|------
uuid | character field | unique, max-length = 36

- Stores UUID of the users who have made submissions. There are no duplicates in the table, no matter how many submissions
one user makes, there is only one object representing the user.

#### 2. The Submission Model

Column | Type | Notes
-------|------|------
user | foreign key | related to the UUID model
os_version | character field | max-length = 10
xcode_version | character field | max-length = 10
os_arch | character field | max-length = 20
build_arch | character field | max-length = 20, default = ''
platform | character field | max-length = 20, default = ''
macports_version | character field | max-length = 10
cxx_stdlib | character field | max-length = 20, default = ''
clt_version | character field | max-length = 100, default = ''
raw_json | json field | stores the entire body of the submission
timestamp | datetime field | stores the time when the submission was made


#### 3. The PortInstallation Model

Column | Type | Notes
-------|------|------
submission | foreign key | related to the Submission model
port | character field | max-length = 100
version | character field | max-length = 100
variants | character field | default = '', max-length = 200
requested | boolean field  | default = False
