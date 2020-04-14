from rest_framework import serializers

from builds.models import BuildHistory, Builder
from port_detail.models import Port, Maintainer, Variant


class MaintainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maintainer
        fields = ('name', 'domain', 'github')


class VariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = ('variant', )


class PortSerializer(serializers.ModelSerializer):
    maintainers = MaintainerSerializer(read_only=True, many=True)
    variants = serializers.SerializerMethodField()

    class Meta:
        model = Port
        fields = ('name', 'portdir', 'categories', 'maintainers', 'version', 'variants')

    def get_variants(self, obj):
        qs = Variant.objects.filter(port=obj)
        variants = VariantSerializer(qs, many=True, read_only=True, context=self.context).data
        return variants


class BuilderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Builder
        fields = ('name', )


class BuildHistorySerializer(serializers.ModelSerializer):
    builder_name = BuilderSerializer(read_only=True)

    class Meta:
        model = BuildHistory
        fields = ('builder_name', 'build_id', 'status', 'time_start', 'time_elapsed', 'watcher_id')


class PortListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Port
        fields = ('name', )
