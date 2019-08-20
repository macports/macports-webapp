## 5. Updating the Ports Data

The app updates ports information incrementally, for the following reasons:
- Updating the entire data of all the ports is a time consuming process.
- To prevent any downtime.

First let us take an overall look at how ports are updated.

To update the ports information incrementally, the app needs two things:
1. Which ports were changed/ updated?
2. The new information, after the change has taken place.

#### Which Ports were Changed/ Updated?

The app maintains a clone of the repository [macports-ports](https://github.com/macports/macports-ports) in the `data`
directory. Every time the cron job to update the port information runs, the script [git_update.py](/app/parsing_scripts/git_update.py)
efficiently finds which paths have changed between any two given commits using information from `git`. These paths are 
nothing, but the `portdir` of the ports which have changed.

The app then saves into the database, git SHASUM of the commit till which the app has been updated. In the next run, 
[git_update.py](/app/parsing_scripts/git_update.py) builds the range of commits using this SHASUM from the database and
the SHASUM of the new commit comes from `portindex.json`, again the changed paths between these two commits are found
and only the ports and subports related to these `portdir` are updated.

#### New Information?

[mprsyncup](https://github.com/macports/macports-infrastructure/blob/master/jobs/mprsyncup) job generates `PortIndex` and
`portindex.json` after each commit, both of these are available through rsync. When the cron job runs, the app fetches
the latest `portindex.json` file, this file also contains the SHASUM of the commit after which it was generated. This
SHASUM is supplied to [git_update.py](/app/parsing_scripts/git_update.py), which returns the set of `portdir` of the
changed ports. Information of these ports is extracted from `portindex.json` and supplied to `Port.update()`, which
updates the information saved in the database.

### How the Process Actually takes place?

A custom Django-admin command has been built into the app ([update-portinfo](/app/ports/management/commands/update-portinfo.py)):

```
python manage.py update-portinfo <new_commit> <old_commit>
```

This command can take the new and old git SHASUM using which the range can be generated. But when the new and old commits
are not provided, the command automatically finds this data from the database (old commit) and from `portindex.json` (new
commit). In fact, the actual updates cron job, runs the bare command.

- The command first fetches the latest, `portindex.json` using `Port.PortIndexUpdateHandler().sync_and_open_file()`.
- If new commit has not been provided as an argument to the command, the command uses the commit from `portindex.json` as
the new commit.
- If old commit has not been provided as an argument to the command, it then uses the commit from database as the old
commit.
- Then it calls `git_update.get_list_of_changed_ports`, which returns the set of `portdir` for the ports which have been
changed between the old and new commit (both inclusive).
- It then loops over the JSON objects for each port obtained from `portindex.json`, and all JSON objects whose `portdir`
is found in the set returned by `git_update.get_list_of_changed_ports` are added to the list `ports_to_be_updated_json`.
- While this looping a dictionary `found_ports_tree` is also generated, whose format is:
    ```python
    {
        "portdir": {
            "port1": True,
            "port2": True,
         },
        "sysutils/mpstats": {
             "mpstats": True
        }   
    }
    ```
- First, we mark those ports as deleted which are available in the database but absent in the dictionary `found_ports_tree`
using the method `Port.mark_deleted()` and set their field `active=False`.
- Then, the list of JSON objects `ports_to_be_updated_json` is passed to `Port.update()` and the actual update is then
carried out by `Port.update()`.
- Finally, the new commit is saved to the database.


### `Port.update()`

This is the actual function that takes in a list of JSON objects and carries out the update of the listed ports. It is a
method of the `Port` model.


##### `Port.update().full_update_ports()`

[Source](/app/ports/models/port.py#L157)
**Port Information:**
All of the basic port information (stored in the [`Port`](/docs/3-MODELS.md#1-the-port-model) model) is reset and the new
information is saved.

**Categories:** For a given port, first all the relations to the [`Category`](/docs/3-MODELS.md#2-the-category-model) model
are cleared and new relations are created again.

**Variants:** We loop over all the related rows in [`Variant`](/docs/3-MODELS.md#4-the-variant-model) table and delete those
which are not present in the new port information. Then, we try to create rows for any variants that might be new.

**Maintainers:** All relations to the [`Maintainer`](/docs/3-MODELS.md#3-the-maintainer-model) model are first cleared and
then new relations are created, during the process of creating new relations, if the maintainer is not already present in
the `Maintainer` model, then a new row is created and then gets related to the port.

##### `Port.update().full_update_dependencies()`

Dependencies are updated by using a separate inner method because of the complex nature of the process.

- First of all, we check if their is any dependency type which no longer exists in the new information and then delete it.
- Then for each dependency type all relations are first cleared, and then added back again while ensuring that any new rows
get created if they do no exist inside the database.
