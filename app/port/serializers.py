from drf_haystack.serializers import HaystackSerializer
from rest_framework import serializers
from django.contrib.postgres.aggregates import ArrayAgg

from maintainer.serializers import MaintainerListSerializer
from port.models import Port, Dependency
from port.search_indexes import PortIndex
from maintainer.search_indexes import MaintainerIndex


# Used by autocomplete search queries
class PortHaystackSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()


class PortSerializer(serializers.ModelSerializer):
    maintainers = MaintainerListSerializer(read_only=True, many=True)
    variants = serializers.SerializerMethodField()
    dependencies = serializers.SerializerMethodField()
    depends_on = serializers.SerializerMethodField()

    class Meta:
        model = Port
        fields = ('name',
                  'portdir',
                  'version',
                  'license',
                  'platforms',
                  'epoch',
                  'replaced_by',
                  'homepage',
                  'description',
                  'long_description',
                  'active',
                  'categories',
                  'maintainers',
                  'variants',
                  'dependencies',
                  'depends_on'
                  )

    def get_variants(self, obj):
        return obj.variants.all().values_list('variant', flat=True)

    def get_dependencies(self, obj):
        return obj.dependent_port.all().values('type').annotate(ports=ArrayAgg('dependencies__name'))

    def get_depends_on(self, obj):
        return Dependency.objects.filter(dependencies__id=obj.id).values('type').annotate(ports=ArrayAgg('port_name__name'))


class SearchSerializer(HaystackSerializer):
    serialize_objects = False
    maintainers = serializers.SerializerMethodField()
    variants = serializers.SerializerMethodField()

    class Meta:
        index_classes = [PortIndex, MaintainerIndex]

        fields = [
            'name',
            'version',
            'description',
            'categories',
            'livecheck_outdated',
            'livecheck_broken',
            'active'
        ]

    def get_maintainers(self, obj):
        return obj.maintainers

    def get_variants(self, obj):
        return obj.variants
