import urllib.request
import ssl
import json
import datetime
import os

from django.db import models
from django.contrib.postgres.fields import JSONField


class Category(models.Model):
    name = models.TextField(primary_key=True)


class PortManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Port(models.Model):
    portdir = models.CharField(max_length=100)
    description = models.TextField(default='')
    homepage = models.URLField(default='')
    epoch = models.BigIntegerField(default=0)
    platforms = models.TextField(null=True)
    categories = models.ManyToManyField(Category, related_name='category', db_index=True)
    long_description = models.TextField(default='')
    version = models.CharField(max_length=100, default='')
    revision = models.IntegerField(default=0)
    closedmaintainer = models.BooleanField(default=False)
    name = models.CharField(max_length=100, db_index=True)
    license = models.CharField(max_length=100, default='')
    replaced_by = models.CharField(max_length=100, null=True)

    objects = PortManager()

    @classmethod
    def load(cls, data):
        def open_portindex_json(path):
            with open(path, "r") as file:
                ports = json.load(file)
            return ports

        # Add All the Categories to the Database using bulk_create
        def load_categories_table(ports):
            categories = set()
            for port in ports:
                try:
                    for category in port['categories']:
                        categories.add(Category(name=category))
                except KeyError:
                    pass
            batch = list(categories)
            Category.objects.bulk_create(batch)
            return

        def load_ports_and_maintainers_table(ports):
            for port in ports:

                # Add Ports to the Database One-by-One
                new_port = Port()
                try:
                    new_port.name = port['name']
                    new_port.portdir = port['portdir']
                    new_port.version = port['version']
                except KeyError:
                    continue

                new_port.description = port.get('description', '')
                new_port.homepage = port.get('homepage', '')
                new_port.epoch = port.get('epoch', 0)
                new_port.platforms = port.get('platforms')
                new_port.long_description = port.get('long_description', '')
                new_port.revision = port.get('revision', 0)
                new_port.closedmaintainer = port.get('closedmaintainer', False)
                new_port.license = port.get('license', '')
                new_port.replaced_by = port.get('replaced_by')
                new_port.save()

                try:
                    new_port.categories.add(*port['categories'])
                except KeyError:
                    pass

                try:
                    for maintainer in port['maintainers']:
                        name = maintainer.get('email', {}).get('name', '')
                        domain = maintainer.get('email', {}).get('domain', '')
                        github = maintainer.get('github', '')

                        maintainer_object, created = Maintainer.objects.get_or_create(
                            name=name,
                            domain=domain,
                            github=github
                        )

                        maintainer_object.ports.add(new_port)
                except KeyError:
                    pass

                try:
                    for variant in port['variants']:
                        variant_object = Variant()
                        variant_object.port = new_port
                        variant_object.variant = variant
                        variant_object.save()
                except KeyError:
                    pass

        def load_dependencies_table(ports):

            def load_depends(list_of_dependencies, type_of_dependency, port):
                dependency = Dependency()
                dependencies = []
                dependency.type = type_of_dependency
                dependency.port_name = port
                for depends in list_of_dependencies:
                    try:
                        dependencies.append(Port.objects.get(name__iexact=depends.rsplit(':', 1)[-1]))
                    except Port.DoesNotExist:
                        print("Failed to append {} as a dependency to {}. Not Found.".format(depends.rsplit(':', 1)[-1],
                                                                                             port.name))
                dependency.save()
                dependency.dependencies.add(*dependencies)

            for port in ports:
                try:
                    port_object = Port.objects.get(name__iexact=port['name'])
                    for dependency_type in ["lib", "extract", "run", "patch", "build", "test", "fetch"]:
                        key = "depends_" + dependency_type
                        if key in port:
                            load_depends(port[key], dependency_type, port_object)

                except Port.DoesNotExist:
                    print("Failed to update dependencies for {}. Port not found in database.".format(port['name']))
        if isinstance(data, list):
            load_ports_and_maintainers_table(data)
            load_categories_table(data)
            load_dependencies_table(data)
        elif isinstance(data, str):
            ports = open_portindex_json(data)
            load_categories_table(ports)
            load_ports_and_maintainers_table(ports)
            load_dependencies_table(ports)

    @classmethod
    def update(cls, data, is_json=True):
        def open_portindex_json(path):
            with open(path, "r") as file:
                ports = json.load(file)
            return ports

        def open_ports_from_list(list_of_ports, path='portindex.json'):
            with open(path, "r") as file:
                all_ports = json.load(file)
            ports_to_be_updated = []
            for port in all_ports:
                if port['name'] in list_of_ports:
                    ports_to_be_updated.append(port)
            return ports_to_be_updated

        def full_update_ports(ports):

            for port in ports:
                port_object, port_created = Port.objects.get_or_create(name=port['name'])

                port_object.portdir = port['portdir']
                port_object.version = port['version']
                port_object.description = port.get('description', '')
                port_object.homepage = port.get('homepage', '')
                port_object.epoch = port.get('epoch', 0)
                port_object.platforms = port.get('platforms', '')
                port_object.long_description = port.get('long_description', '')
                port_object.revision = port.get('revision', 0)
                port_object.closedmaintainer = port.get('closedmaintainer', False)
                port_object.license = port.get('license', '')
                port_object.replaced_by = port.get('replaced_by')
                port_object.save()

                try:
                    port_object.categories.clear()
                    for category in port['categories']:
                        category_object, category_created = Category.objects.get_or_create(name=category)
                        port_object.categories.add(category_object)
                except KeyError:
                    pass

                try:
                    variant_objects = Variant.objects.filter(port_id=port_object.id)

                    for variant_object in variant_objects:
                        if variant_object not in port['variants']:
                            variant_object.delete()

                    for variant in port['variants']:
                        v_obj, created = Variant.objects.get_or_create(port_id=port_object.id, variant=variant)
                except KeyError:
                    pass

                try:
                    port_object.maintainers.clear()
                    for maintainer in port['maintainers']:
                        name = maintainer.get('email', {}).get('name', '')
                        domain = maintainer.get('email', {}).get('domain', '')
                        github = maintainer.get('github', '')

                        maintainer_object, created = Maintainer.objects.get_or_create(
                            name=name,
                            domain=domain,
                            github=github
                        )

                        maintainer_object.ports.add(port_object)
                except KeyError:
                    pass

        def full_update_dependencies(ports):

            for port in ports:
                try:
                    all_dependency_objects = Dependency.objects.filter(port_name__name__iexact=port['name'])
                    port_object = Port.objects.get(name=port['name'])

                    # Delete the dependency types from database that no longer exist in
                    for dependency_object in all_dependency_objects:
                        key = "depends_" + dependency_object.type
                        if key not in port:
                            dependency_object.delete()

                    for dependency_type in ["lib", "extract", "run", "patch", "build", "test", "fetch"]:
                        key = "depends_" + dependency_type
                        if key in port:
                            obj, created = Dependency.objects.get_or_create(port_name_id=port_object.id,
                                                                            type=dependency_type)
                            obj.type = dependency_type
                            obj.port_name = port_object
                            obj.dependencies.clear()
                            dependencies = []

                            for depends in port[key]:
                                try:
                                    dependencies.append(Port.objects.get(name__iexact=depends.rsplit(':', 1)[-1]))
                                except Port.DoesNotExist:
                                    print("Failed to append {} as a dependency to {}. Not Found.".format(
                                        depends.rsplit(':', 1)[-1],
                                        port.name))
                            obj.save()
                            obj.dependencies.add(*dependencies)

                except Port.DoesNotExist:
                    print(
                        "Failed to update depencies for {}. Port does not exist in the database.".format(port['name']))

        # Takes in a list of JSON objects and runs the updates
        def run_updates(ports):
            full_update_ports(ports)
            full_update_dependencies(ports)

        # Block to find type of passed "data" and run updates accordingly
        # ============ START ============

        # If the passed object is a valid path, open it and parse the JSON objects
        if isinstance(data, str):
            if os.path.exists(data):
                ports = open_portindex_json(data)
                run_updates(ports)
            else:
                print('File "{}" not found.'.format(data))

        # If the passed object is a list
        elif isinstance(data, list):
            # If the passed list contains JSON objects, run the updates directly
            if is_json:
                full_update_ports(data)
                full_update_dependencies(data)

            # If the passed list contains names of ports, first fetch corresponding JSON objects then run the updates
            else:
                ports = open_ports_from_list(data)
                run_updates(ports)

        # ============ END ==============


class Dependency(models.Model):
    port_name = models.ForeignKey(Port, on_delete=models.CASCADE, related_name="dependent_port")
    dependencies = models.ManyToManyField(Port)
    type = models.CharField(max_length=100)

    class Meta:
        unique_together = [['port_name', 'type']]

        indexes = [
            models.Index(fields=['port_name'])
        ]


class Variant(models.Model):
    port = models.ForeignKey(Port, on_delete=models.CASCADE, related_name='ports')
    variant = models.CharField(max_length=100, default='')


class Maintainer(models.Model):
    name = models.CharField(max_length=50, default='')
    domain = models.CharField(max_length=50, default='')
    github = models.CharField(max_length=50, default='')
    ports = models.ManyToManyField(Port, related_name='maintainers')

    objects = PortManager()

    class Meta:
        unique_together = [['name', 'domain', 'github']]

        indexes = [
            models.Index(fields=['github']),
            models.Index(fields=['name', 'domain'])
        ]


class Builder(models.Model):
    name = models.CharField(max_length=100, db_index=True)


class BuildHistory(models.Model):
    builder_name = models.ForeignKey(Builder, on_delete=models.CASCADE)
    build_id = models.IntegerField()
    status = models.CharField(max_length=50)
    port_name = models.CharField(max_length=100)
    time_start = models.DateTimeField()
    time_elapsed = models.TimeField(null=True)
    watcher_id = models.IntegerField()

    class Meta:
        indexes = [
            models.Index(fields=['port_name', 'builder_name', '-build_id']),
            models.Index(fields=['port_name', 'status', 'builder_name']),
            models.Index(fields=['port_name', 'builder_name']),
            models.Index(fields=['-time_start']),
            models.Index(fields=['port_name']),
            models.Index(fields=['status']),
            models.Index(fields=['builder_name'])
        ]

    @classmethod
    def populate(cls):
        builders = Builder.objects.values_list('name', flat=True)
        url_prefix = 'https://build.macports.org'

        def get_url_json(builder_name, build_number):
            return '{}/json/builders/ports-{}-builder/builds/{}'.format(url_prefix, builder_name, build_number)

        def get_url_build(builder_name, build_number):
            return '{}/builders/ports-{}-builder/builds/{}'.format(url_prefix, builder_name, build_number)

        def get_data_from_url(url):
            gcontext = ssl.SSLContext()
            with urllib.request.urlopen(url, context=gcontext) as u:
                data = json.loads(u.read().decode())
            return data

        def get_build_properties(array):
            properties = {}
            for prop in array['properties']:
                properties[prop[0]] = prop[1]
            return properties

        def return_summary(builder_name, build_number, build_data):
            data = {}

            properties = get_build_properties(build_data)
            port_name = properties['portname']
            status = ' '.join(build_data['text'])
            time_start = build_data['times'][0]
            time_build = float(build_data['times'][1]) - float(build_data['times'][0])

            data['name'] = port_name
            data['url'] = get_url_build(builder_name, build_number)
            data['watcher_id'] = properties['triggered_by'].split('/')[6]
            data['watcher_url'] = properties['triggered_by']
            data['status'] = status
            data['builder'] = builder_name
            data['buildnr'] = build_number
            data['time_start'] = str(datetime.datetime.fromtimestamp(int(float(time_start)), tz=datetime.timezone.utc))
            data['buildtime'] = str(
                datetime.timedelta(seconds=int(float(time_build)))) if time_build is not -1 else None

            return data

        def load_database(data):
            builder = Builder.objects.get(name=data['builder'])
            build = BuildHistory()
            build.port_name = data['name']
            build.status = data['status']
            build.build_id = data['buildnr']
            build.time_start = data['time_start']
            build.time_elapsed = data['buildtime']
            build.builder_name = builder
            build.build_url = data['url']
            build.watcher_url = data['watcher_url']
            build.watcher_id = data['watcher_id']
            build.save()

        fulldata = {}

        def add_to_summary(data):
            if not data['name'] in fulldata:
                fulldata[data['name']] = {}
            if not data['builder'] in fulldata[data['name']]:
                fulldata[data['name']][data['builder']] = []
            fulldata[data['name']][data['builder']].append(data)

        for buildername in builders:
            print()

            # fetch the last build first in order to figure out its number
            last_build_data = get_data_from_url(get_url_json(buildername, -1))
            last_build_number = last_build_data['number']
            build_number_loaded = BuildHistory.objects.filter(builder_name__name=buildername).order_by('-build_id')
            if build_number_loaded:
                build_in_database = build_number_loaded[0].build_id + 1
            else:
                build_in_database = last_build_number - 9999

            for build_number in range(build_in_database, last_build_number):
                build_data = get_data_from_url(get_url_json(buildername, build_number))
                build_data_summary = return_summary(buildername, build_number, build_data)
                add_to_summary(build_data_summary)
                load_database(build_data_summary)


# Contains the latest state of the JSON submitted by the mpstats for user
class User(models.Model):
    uuid = models.CharField(max_length=36, db_index=True)
    osx_version = models.CharField(max_length=10)
    macports_version = models.CharField(max_length=10)
    xcode_version = models.CharField(max_length=10)
    os_arch = models.CharField(max_length=10)
    full_json = JSONField()
    updated_at = models.DateTimeField(auto_now=True)


class OSDistribution(models.Model):
    osx_version = models.CharField(max_length=20, db_index=True)
    month = models.IntegerField(db_index=True)
    year = models.IntegerField(db_index=True)
    users = models.ManyToManyField(User, related_name='users')


class Commit(models.Model):
    hash = models.CharField(max_length=50)
    updated_at = models.DateTimeField(auto_now=True)


class UUID(models.Model):
    uuid = models.CharField(max_length=36, db_index=True)


class Submission(models.Model):
    user = models.ForeignKey(UUID, on_delete=models.CASCADE)
    os_version = models.CharField(max_length=10)
    xcode_version = models.CharField(max_length=10)
    os_arch = models.CharField(max_length=20)
    macports_version = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user']),
            models.Index(fields=['user', '-timestamp']),
        ]

    @classmethod
    def populate(cls, json_object):
        uuid_obj, created = UUID.objects.get_or_create(uuid=json_object['id'])
        sub = Submission()
        sub.user = uuid_obj
        sub.os_version = json_object['os']['osx_version']
        sub.xcode_version = json_object['os']['xcode_version']
        sub.os_arch = json_object['os']['os_arch']
        sub.macports_version = json_object['os']['macports_version']
        sub.save()
        return sub.id


class PortInstallation(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    port = models.CharField(max_length=100)
    version = models.CharField(max_length=100)
    requested = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['submission']),
            models.Index(fields=['port'])
        ]

    @classmethod
    def populate(cls, port_json, submission_id):
        ports = []
        for port in port_json:
            obj = PortInstallation()
            obj.submission_id = submission_id
            obj.port = port['name']
            obj.version = port['version']
            obj.requested = True if port.get('requested') is "true" else False
            ports.append(obj)
        PortInstallation.objects.bulk_create(ports)
        return
