from distutils.version import LooseVersion

from django.db import models
from django.contrib.postgres.fields import JSONField


class UUID(models.Model):
    uuid = models.CharField(max_length=36, db_index=True)


class Submission(models.Model):
    user = models.ForeignKey(UUID, on_delete=models.CASCADE)
    os_version = models.CharField(max_length=10)
    xcode_version = models.CharField(max_length=10)
    os_arch = models.CharField(max_length=20)
    build_arch = models.CharField(max_length=20, default='')
    platform = models.CharField(max_length=20, default='')
    macports_version = models.CharField(max_length=10)
    cxx_stdlib = models.CharField(max_length=20, default='')
    clt_version = models.CharField(max_length=100, default='')
    raw_json = JSONField(default=dict)
    timestamp = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['os_version']),
            models.Index(fields=['os_version', 'os_arch']),
            models.Index(fields=['os_version', 'xcode_version']),
            models.Index(fields=['os_arch']),
            models.Index(fields=['macports_version']),
            models.Index(fields=['cxx_stdlib']),
            models.Index(fields=['build_arch']),
            models.Index(fields=['clt_version'])
        ]

    @classmethod
    def populate(cls, json_object, timestamp):
        uuid_obj, created = UUID.objects.get_or_create(uuid=json_object['id'])
        sub = Submission()
        sub.user = uuid_obj
        os_version = json_object['os'].get('osx_version')
        cxx_stdlib = json_object['os'].get('cxx_stdlib')
        if cxx_stdlib is None and LooseVersion(os_version) >= LooseVersion('10.9'):
            cxx_stdlib = "libc++"

        sub.os_version = os_version
        sub.xcode_version = json_object['os'].get('xcode_version')
        sub.os_arch = json_object['os'].get('os_arch')
        sub.macports_version = json_object['os'].get('macports_version')
        sub.cxx_stdlib = cxx_stdlib
        sub.build_arch = json_object['os'].get('build_arch')
        sub.platform = json_object['os'].get('os_platform')
        sub.clt_version = json_object['os'].get('clt_version')
        sub.raw_json = json_object
        sub.timestamp = timestamp
        sub.save()
        return sub.id


class PortInstallation(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    port = models.CharField(max_length=100)
    version = models.CharField(max_length=100)
    variants = models.CharField(max_length=200, default='')
    requested = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['submission']),
            models.Index(fields=['port']),
            models.Index(fields=['variants'])
        ]

    @classmethod
    def populate(cls, port_json, submission_id):
        ports = []
        for port in port_json:
            obj = PortInstallation()
            obj.submission_id = submission_id
            obj.port = port['name']
            obj.version = port['version']
            obj.variants = port.get('variants')
            obj.requested = True if port.get('requested') == "true" else False
            ports.append(obj)
        PortInstallation.objects.bulk_create(ports)
        return
