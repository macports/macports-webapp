import urllib.request
import ssl
import json
import datetime

from django.db import models

from MacPorts.config import BUILDERS_JSON_URL, BUILDBOT_URL_PREFIX, BUILDS_FETCHED_COUNT


class Builder(models.Model):
    name = models.CharField(max_length=100, db_index=True)


class BuildHistory(models.Model):
    builder_name = models.ForeignKey(Builder, on_delete=models.CASCADE)
    build_id = models.IntegerField()
    status = models.CharField(max_length=50)
    port_name = models.CharField(max_length=100)
    time_start = models.DateTimeField()
    time_elapsed = models.DurationField(null=True)
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
        url_prefix = BUILDBOT_URL_PREFIX

        def get_url_json(builder_name, build_number):
            return '{}/json/builders/ports-{}-builder/builds/{}'.format(url_prefix, builder_name, build_number)

        def get_url_build(builder_name, build_number):
            return '{}/builders/ports-{}-builder/builds/{}'.format(url_prefix, builder_name, build_number)

        def get_data_from_url(url):
            gcontext = ssl.SSLContext()
            try:
                with urllib.request.urlopen(url, context=gcontext) as u:
                    data = json.loads(u.read().decode())
                return data
            except urllib.error.URLError:
                return {}

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

        for buildername in builders:
            # fetch the last build first in order to figure out its number
            last_build_data = get_data_from_url(get_url_json(buildername, -1))
            if not last_build_data:
                continue
            last_build_number = last_build_data['number']
            build_number_loaded = BuildHistory.objects.filter(builder_name__name=buildername).order_by('-build_id')
            if build_number_loaded:
                build_in_database = build_number_loaded[0].build_id + 1
            else:
                build_in_database = last_build_number - BUILDS_FETCHED_COUNT

            for build_number in range(build_in_database, last_build_number):
                build_data = get_data_from_url(get_url_json(buildername, build_number))
                if not build_data:
                    break
                build_data_summary = return_summary(buildername, build_number, build_data)
                load_database(build_data_summary)

    @classmethod
    def populate_builders(cls):
        gcontext = ssl.SSLContext()
        with urllib.request.urlopen(BUILDERS_JSON_URL, context=gcontext) as u:
            data = json.loads(u.read().decode())

        builders = []
        for key in data:
            if not key.split('-')[0] == 'ports':
                continue

            if not key.split('-')[2] == 'builder':
                continue

            if not len(data[key]['cachedBuilds']) > 0:
                continue

            builders.append(Builder(name=key.split('-')[1]))
        Builder.objects.bulk_create(builders)
