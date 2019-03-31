from django.db import models

class Category(models.Model):
    name = models.TextField(primary_key=True)

class Port(models.Model):
    portdir = models.CharField(max_length=100)
    variants = models.TextField(default='')
    description = models.TextField(default='')
    homepage = models.URLField(default='')
    epoch = models.TextField(default='')
    platforms = models.TextField(default='')
    categories = models.ManyToManyField(Category, related_name='category', db_index=True)
    long_description = models.TextField(default='')
    depends_extract = models.TextField(default='')
    version = models.CharField(max_length=100)
    revision = models.TextField(default='')
    maintainers = models.TextField(default='')
    name = models.CharField(max_length=100, db_index=True)
    license = models.CharField(max_length=100)
    depends_lib = models.TextField(default='')
    depends_build = models.TextField(default='')
    installs_libs = models.TextField(default='')
    depends_fetch = models.TextField(default='')
    depends_run = models.TextField(default='')
    conflicts = models.TextField(default='')
    replaced_by = models.TextField(default='')
    depends_test = models.TextField(default='')
    depends_patch = models.TextField(default='')
    subports = models.TextField(default='')

class BuildHistory(models.Model):
    builder_name = models.CharField(max_length=50, db_index=True)
    build_id = models.IntegerField()
    status = models.CharField(max_length=50)
    port_name = models.CharField(max_length=50,db_index=True)
    time_start = models.CharField(max_length=50)
    time_elapsed = models.CharField(max_length=50)
    build_url = models.URLField(default='')
    watcher_id = models.IntegerField()
    watcher_url = models.URLField()








