import urllib.request
import ssl
import json
import datetime

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

    class Load:
        def open_portindex_json(self, path):
            with open(path, "r") as file:
                ports = json.load(file)
            return ports

        # Add All the Categories to the Database using bulk_create
        def load_categories_table(self, ports):
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

        def load_ports_and_maintainers_table(self, ports):
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

        def load_dependencies_table(self, ports):

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

    class Update:
        def open_portindex_json(self, path='portindex.json'):
            with open(path, "r") as file:
                ports = json.load(file)
            return ports

        def open_ports_from_list(self, list_of_ports, path='portindex.json'):
            with open(path, "r") as file:
                all_ports = json.load(file)
            ports_to_be_updated = []
            for port in all_ports:
                if port['name'] in list_of_ports:
                    ports_to_be_updated.append(port)
            return ports_to_be_updated

        def full_update_ports(self, ports):

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

        def full_update_dependencies(self, ports):

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


class Dependency(models.Model):
    port_name = models.ForeignKey(Port, on_delete=models.CASCADE, related_name="dependent_port")
    dependencies = models.ManyToManyField(Port, db_index=True)
    type = models.CharField(max_length=100)

    class Meta:
        unique_together = [['port_name', 'type']]


class Variant(models.Model):
    port = models.ForeignKey(Port, on_delete=models.CASCADE, related_name='ports')
    variant = models.CharField(max_length=100, default='')


class Maintainer(models.Model):
    name = models.CharField(max_length=50, db_index=True, default='')
    domain = models.CharField(max_length=50, db_index=True, default='')
    github = models.CharField(max_length=50, db_index=True, default='')
    ports = models.ManyToManyField(Port, related_name='maintainers', db_index=True)

    objects = PortManager()

    class Meta:
        unique_together = [['name', 'domain', 'github']]


class Builder(models.Model):
    name = models.CharField(max_length=100, db_index=True)


class BuildHistory(models.Model):
    builder_name = models.ForeignKey(Builder, on_delete=models.CASCADE, db_index=True)
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
            models.Index(fields=['status'])
        ]

    class Populate:
        builders = Builder.objects.values_list('name', flat=True)
        url_prefix = 'https://build.macports.org'

        def get_url_json(self, builder_name, build_number):
            return '{}/json/builders/ports-{}-builder/builds/{}'.format(self.url_prefix, builder_name, build_number)

        def get_url_build(self, builder_name, build_number):
            return '{}/builders/ports-{}-builder/builds/{}'.format(self.url_prefix, builder_name, build_number)

        def get_data_from_url(self, url):
            gcontext = ssl.SSLContext()
            with urllib.request.urlopen(url, context=gcontext) as u:
                data = json.loads(u.read().decode())
            return data

        def get_build_properties(self, array):
            properties = {}
            for prop in array['properties']:
                properties[prop[0]] = prop[1]
            return properties

        def get_build_steps(self, array):
            steps = {}
            for step in array['steps']:
                steps[step['name']] = step
            return steps

        def return_summary(self, builder_name, build_number, build_data):
            data = {}

            properties = self.get_build_properties(build_data)
            port_name = properties['portname']
            status = ' '.join(build_data['text'])
            time_start = build_data['times'][0]
            time_build = float(build_data['times'][1]) - float(build_data['times'][0])

            data['name'] = port_name
            data['url'] = self.get_url_build(builder_name, build_number)
            data['watcher_id'] = properties['triggered_by'].split('/')[6]
            data['watcher_url'] = properties['triggered_by']
            data['status'] = status
            data['builder'] = builder_name
            data['buildnr'] = build_number
            data['time_start'] = str(datetime.datetime.fromtimestamp(int(float(time_start)), tz=datetime.timezone.utc))
            data['buildtime'] = str(
                datetime.timedelta(seconds=int(float(time_build)))) if time_build is not -1 else None

            return data

        def load_database(self, data):
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

        def add_to_summary(self, data):
            if not data['name'] in self.fulldata:
                self.fulldata[data['name']] = {}
            if not data['builder'] in self.fulldata[data['name']]:
                self.fulldata[data['name']][data['builder']] = []
            self.fulldata[data['name']][data['builder']].append(data)

        def fetch(self):
            for buildername in self.builders:
                print()

                # fetch the last build first in order to figure out its number
                last_build_data = self.get_data_from_url(self.get_url_json(buildername, -1))
                last_build_number = last_build_data['number']
                build_number_loaded = BuildHistory.objects.filter(builder_name__name=buildername).order_by('-build_id')
                if build_number_loaded:
                    build_in_database = build_number_loaded[0].build_id + 1
                else:
                    build_in_database = last_build_number - 9999

                for build_number in range(build_in_database, last_build_number):
                    build_data = self.get_data_from_url(self.get_url_json(buildername, build_number))
                    build_data_summary = self.return_summary(buildername, build_number, build_data)
                    self.add_to_summary(build_data_summary)
                    self.load_database(build_data_summary)


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
