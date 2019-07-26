from django.db import models
from django.contrib.postgres.fields import JSONField


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


class UUID(models.Model):
    uuid = models.CharField(max_length=36, db_index=True)


class Submission(models.Model):
    user = models.ForeignKey(UUID, on_delete=models.CASCADE)
    os_version = models.CharField(max_length=10)
    xcode_version = models.CharField(max_length=10)
    os_arch = models.CharField(max_length=20)
    macports_version = models.CharField(max_length=10)
    cxx_stdlib = models.CharField(max_length=20, default='libc++')
    timestamp = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['os_version']),
            models.Index(fields=['os_arch']),
            models.Index(fields=['macports_version']),
            models.Index(fields=['cxx_stdlib']),
        ]

    @classmethod
    def populate(cls, json_object, timestamp):
        uuid_obj, created = UUID.objects.get_or_create(uuid=json_object['id'])
        sub = Submission()
        sub.user = uuid_obj
        sub.os_version = json_object['os']['osx_version']
        sub.xcode_version = json_object['os']['xcode_version']
        sub.os_arch = json_object['os']['os_arch']
        sub.macports_version = json_object['os']['macports_version']
        sub.cxx_stdlib = json_object['os']['cxx_stdlib']
        sub.timestamp = timestamp
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
            obj.requested = True if port.get('requested') == "true" else False
            ports.append(obj)
        PortInstallation.objects.bulk_create(ports)
        return
