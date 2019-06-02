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
    status = models.CharField(max_length=50)
    port_name = models.CharField(max_length=50,db_index=True)
    time_start = models.CharField(max_length=50)
    time_elapsed = models.CharField(max_length=50)
    build_url = models.URLField(default='')
    watcher_id = models.IntegerField()
    watcher_url = models.URLField()


# Contains the latest state of the JSON submitted by the mpstats for user
class User(models.Model):
    uuid = models.CharField(max_length=36, db_index=True)
    osx_version = models.CharField(max_length=10)
    macports_version = models.CharField(max_length=10)
    xcode_version = models.CharField(max_length=10)
    os_arch = models.CharField(max_length=10)
    full_json = JSONField()
    updated_at = models.DateTimeField(auto_now=True)
