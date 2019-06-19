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
    status = models.CharField(max_length=50, db_index=True)
    port_name = models.CharField(max_length=50, db_index=True)
    time_start = models.DateTimeField(db_index=True)
    time_elapsed = models.TimeField(null=True)
    watcher_id = models.IntegerField()

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
