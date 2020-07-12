import json
import subprocess

from django.db import models, transaction
from django.urls import reverse
from django.contrib.auth.models import User
from notifications.signals import notify

from category.models import Category
from maintainer.models import Maintainer
from variant.models import Variant
from port.notif import generate_notifications_verb
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    subscribers = models.ManyToManyField(User, related_name='ports', verbose_name="Subscribers of the port")

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

    def is_followed(self, request):
        if request.user.is_authenticated:
            usr = request.user
        else:
            return False

        if self.subscribers.all().filter(id=usr.id).exists():
            return True
        return False

    @classmethod
    def add_or_update(cls, data):
        @transaction.atomic
        def load_ports_table(ports):
            for port in ports:
                # any json object missing name, portdir, version will be ignored
                try:
                    name = port['name']
                    portdir = port['portdir']
                    version = port['version']
                except KeyError:
                    continue

                # get or create an object for this port
                port_object, port_created = Port.objects.get_or_create(name__iexact=name, defaults={'name': name})

                # cache the original object for comparison
                old_object = {
                    'version': port_object.version,
                    'replaced_by': port_object.replaced_by,
                    'license': port_object.license
                }

                # add or update rest of the fields
                port_object.portdir = portdir
                port_object.version = version
                port_object.description = port.get('description', '')
                port_object.homepage = port.get('homepage', '')
                port_object.epoch = port.get('epoch', 0)
                port_object.platforms = port.get('platforms')
                port_object.long_description = port.get('long_description', '')
                port_object.revision = port.get('revision', 0)
                port_object.closedmaintainer = port.get('closedmaintainer', False)
                port_object.license = port.get('license', '')
                port_object.replaced_by = port.get('replaced_by')
                port_object.active = True
                port_object.save()

                notification_verb = generate_notifications_verb(old_object, port_object)
                if not notification_verb == "":
                    notify.send(
                        port_object,
                        recipient=port_object.subscribers.all(),
                        verb=notification_verb,
                        portdir=port_object.portdir,
                        version=port_object.version
                    )

                # first remove any related category and then add
                port_object.categories.clear()  # remove any related objects
                categories = set()
                for category in port.get('categories', []):
                    category_object, created = Category.objects.get_or_create(name__iexact=category, defaults={'name': category})
                    categories.add(category_object)
                port_object.categories.add(*categories)

                # remove any related maintainers and then add all
                port_object.maintainers.clear()
                for maintainer in port.get('maintainers', []):
                    maintainer_name = maintainer.get('email', {}).get('name', '')
                    maintainer_domain = maintainer.get('email', {}).get('domain', '')
                    maintainer_github = maintainer.get('github', '')

                    maintainer_object, created = Maintainer.objects.get_or_create(
                        name__iexact=maintainer_name,
                        domain__iexact=maintainer_domain,
                        github__iexact=maintainer_github,
                        defaults={
                            'name': maintainer_name,
                            'domain': maintainer_domain,
                            'github': maintainer_github
                        }
                    )
                    maintainer_object.ports.add(port_object)

                # delete all related variants and then add all
                port_object.variants.all().delete()
                for variant in port.get('variants', []):
                    v_obj, created = Variant.objects.get_or_create(port_id=port_object.id, variant__iexact=variant, defaults={'variant': variant})

                print("Updated port: ", port_object.name)

        @transaction.atomic
        def load_dependencies_table(ports):
            # To prevent repetitive queries for adding a relation between port and its dependency
            # we prepare a map of port names and their primary keys in advance
            port_id_map = {}
            for port_object in Port.objects.all():
                port_id_map[port_object.name.lower()] = port_object.id

            def load_depends(port_id, type_of_dependency, list_of_dependencies):
                d_object, created = Dependency.objects.get_or_create(type=type_of_dependency, port_name_id=port_id)
                d_object.dependencies.clear()
                dependencies = set()
                for i in list_of_dependencies:
                    try:
                        dependency_name = i.rsplit(':', 1)[-1]
                        dependencies.add(port_id_map[dependency_name.lower()])
                    except KeyError:
                        pass
                d_object.dependencies.add(*dependencies)

            for port in ports:
                try:
                    name = port['name']
                except KeyError:
                    continue
                try:
                    port_object = Port.objects.get(name=name)
                except Port.DoesNotExist:
                    continue

                for dependency_type in ["lib", "extract", "run", "patch", "build", "test", "fetch"]:
                    key = "depends_" + dependency_type
                    if key in port:
                        load_depends(port_object.id, dependency_type, port[key])

                print("Updated port dependencies: ", port['name'])

        def run(ports):
            load_ports_table(ports)
            load_dependencies_table(ports)

        run(data)

    @classmethod
    def mark_deleted(cls, dict_of_portdirs_with_ports):
        for portdir in dict_of_portdirs_with_ports:
            for port in Port.objects.filter(portdir__iexact=portdir).only('portdir', 'name', 'active'):
                if port.name.lower() not in dict_of_portdirs_with_ports[portdir]:
                    port.active = False
                    notify.send(port, recipient=port.subscribers.all(), verb="Port has been deleted.")
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
    port = models.OneToOneField(Port, on_delete=models.CASCADE, related_name='livecheck')
    result = models.TextField(null=True, verbose_name="Result of the last livecheck for the port. Only stored if new version is available")
    has_updates = models.BooleanField(default=False, verbose_name="True if updates are available for the port.")
    error = models.TextField(null=True, verbose_name="Error thrown by livecheck, defaults to Null if no error encountered")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Timestamp when livecheck was last for the port")

    class Meta:
        db_table = "livecheck"
        verbose_name = "Livecheck"
        indexes = [
            models.Index(fields=['updated_at']),
            models.Index(fields=['has_updates']),
            models.Index(fields=['has_updates', 'updated_at'])
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
