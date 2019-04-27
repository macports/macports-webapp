from django.db import models

class Category(models.Model):
    name = models.TextField(primary_key=True)


class PortManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Port(models.Model):
    portdir = models.CharField(max_length=100)
    variants = models.TextField(default='')
    description = models.TextField(default='')
    homepage = models.URLField(default='')
    epoch = models.TextField(default='')
    platforms = models.TextField(default='')
    categories = models.ManyToManyField(Category, related_name='category', db_index=True)
    long_description = models.TextField(default='')
    version = models.CharField(max_length=100)
    revision = models.IntegerField(default=0)
    closedmaintainer = models.BooleanField()
    name = models.CharField(max_length=100, db_index=True)
    license = models.CharField(max_length=100)
    replaced_by = models.CharField(max_length=100)

    objects = PortManager()


class Dependency(models.Model):
    port_name = models.ForeignKey(Port, on_delete=models.CASCADE, related_name="dependent_port", db_index=True)
    dependencies = models.ManyToManyField(Port, db_index=True)
    type = models.CharField(max_length=100)


class Maintainer(models.Model):
    name = models.CharField(max_length=50, db_index=True)
    domain = models.CharField(max_length=50, db_index=True)
    github = models.CharField(max_length=50, db_index=True)
    ports = models.ManyToManyField(Port, related_name='maintainers', db_index=True)

    objects = PortManager()


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







