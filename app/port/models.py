import json
import os
import subprocess

from django.db import models, transaction
from django.urls import reverse
import config


class PortManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class ActivePortsManager(models.Manager):
    def get_queryset(self):
        return super(ActivePortsManager, self).get_queryset().filter(active=True)


class Port(models.Model):
    portdir = models.CharField(max_length=100)
    description = models.TextField(default='')
    homepage = models.URLField(default='')
    epoch = models.BigIntegerField(default=0)
    platforms = models.TextField(null=True)
    categories = models.ManyToManyField('category.Category', related_name='ports', db_index=True)
    long_description = models.TextField(default='')
    version = models.CharField(max_length=100, default='')
    revision = models.IntegerField(default=0)
    closedmaintainer = models.BooleanField(default=False)
    name = models.CharField(max_length=100, db_index=True)
    license = models.CharField(max_length=100, default='')
    replaced_by = models.CharField(max_length=100, null=True)
    active = models.BooleanField(default=True)

    objects = PortManager()
    get_active = ActivePortsManager()

    def __str__(self):
        return '%s' % self.name

    class Meta:
        db_table = "port"
        verbose_name = "Port"
        verbose_name_plural = "Ports"

    def get_absolute_url(self):
        return reverse('port_detail', args=[str(self.name)])

    @classmethod
    def load(cls, data):
        def open_portindex_json(path):
            with open(path, "r", encoding='utf-8') as file:
                data = json.load(file)
            return data['ports']

        # Add All the Categories to the Database using bulk_create
        def load_categories_table(ports):
            from category.models import Category

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

        port_id_map = {}

        @transaction.atomic
        def load_ports_and_maintainers_table(ports):
            from maintainer.models import Maintainer
            from variant.models import Variant

            port_id = 1
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
                port_id_map[port['name']] = port_id
                port_id += 1

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

        @transaction.atomic
        def load_dependencies_table(ports):
            def load_depends(port_id, type_of_dependency, list_of_dependencies):
                obj = Dependency()
                dependencies = []
                obj.type = type_of_dependency
                obj.port_name_id = port_id
                for i in list_of_dependencies:
                    try:
                        dependency_name = i.rsplit(':', 1)[-1]
                        dependencies.append(port_id_map[dependency_name])
                    except KeyError:
                        pass
                obj.save()
                obj.dependencies.add(*dependencies)

            for port in ports:
                try:
                    port_id = port_id_map[port['name']]
                    for dependency_type in ["lib", "extract", "run", "patch", "build", "test", "fetch"]:
                        key = "depends_" + dependency_type
                        if key in port:
                            load_depends(port_id, dependency_type, port[key])

                except KeyError:
                    pass

        def populate(ports):
            load_categories_table(ports)
            load_ports_and_maintainers_table(ports)
            load_dependencies_table(ports)

        # If list of JSON objects in passed, start populating
        if isinstance(data, list):
            populate(data)
        # If a path to JSON file is provided, open the file and then start populating
        elif isinstance(data, str):
            ports = open_portindex_json(data)
            populate(ports)

    @classmethod
    def update(cls, data):
        from category.models import Category
        from maintainer.models import Maintainer
        from variant.models import Variant

        def open_portindex_json(path):
            with open(path, "r", encoding='utf-8') as file:
                data = json.load(file)
            return data['ports']

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
                port_object.active = True
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
                                        port['name']))
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

        # If a valid path is passed, open it and parse the JSON objects
        if isinstance(data, str):
            if os.path.exists(data):
                ports = open_portindex_json(data)
                run_updates(ports)
            else:
                print('File "{}" not found.'.format(data))

        # If a list is passed, run the updates directly
        elif isinstance(data, list):
            run_updates(data)

        # ============ END ==============

    @classmethod
    def mark_deleted(cls, dict_of_portdirs_with_ports):
        for portdir in dict_of_portdirs_with_ports:
            for port in Port.objects.filter(portdir__iexact=portdir).only('portdir', 'name', 'active'):
                if port.name not in dict_of_portdirs_with_ports[portdir]:
                    port.active = False
                    port.save()

    class PortIndexUpdateHandler:
        @staticmethod
        def sync_and_open_file():
            return_code = subprocess.call([config.RSYNC, config.PORTINDEX_SOURCE, config.PORTINDEX_JSON])
            if return_code != 0:
                return {}
            with open(config.PORTINDEX_JSON, "r", encoding='utf-8') as file:
                data = json.load(file)
            return data


class Dependency(models.Model):
    port_name = models.ForeignKey(Port, on_delete=models.CASCADE, related_name="dependent_port")
    dependencies = models.ManyToManyField(Port)
    type = models.CharField(max_length=100)

    class Meta:
        db_table = "dependency"
        verbose_name = "Dependency"
        verbose_name_plural = "Dependencies"
        unique_together = [['port_name', 'type']]
        indexes = [
            models.Index(fields=['port_name'])
        ]


class LiveCheck(models.Model):
    port = models.ForeignKey(Port, on_delete=models.CASCADE, related_name='livecheck')
    result = models.TextField(null=True, verbose_name="Result of the last livecheck for the port")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Timestamp when livecheck was last for the port")

    class Meta:
        db_table = "livecheck"
        verbose_name = "Livecheck"
        indexes = [
            models.Index(fields=['updated_at'])
        ]


class LastPortIndexUpdate(models.Model):
    git_commit_hash = models.CharField(max_length=50, verbose_name="Commit hash till which update was done")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Timestamp when update completed")

    class Meta:
        db_table = "portindex_update"
        verbose_name = "PortIndex Update"
        verbose_name_plural = "PortIndex Updates"

    @classmethod
    def update_or_create_first_object(cls, commit_hash):
        first_object = LastPortIndexUpdate.objects.all().first()
        if first_object is None:
            LastPortIndexUpdate.objects.create(git_commit_hash=commit_hash)
        else:
            first_object.git_commit_hash = commit_hash
            first_object.save()
