from rest_framework import serializers

from ports.models import Port, Maintainer, Variant, BuildHistory, Builder


class MaintainerSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Maintainer
        fields = ('name', 'domain', 'github')


class VariantSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = ('variant', )


class PortSerialiser(serializers.ModelSerializer):
    maintainers = MaintainerSerialiser(read_only=True, many=True)
    variants = serializers.SerializerMethodField()

    class Meta:
        model = Port
        fields = ('name', 'portdir', 'categories', 'maintainers', 'version', 'variants')

    def get_variants(self, obj):
        qs = Variant.objects.filter(port=obj)
        variants = VariantSerialiser(qs, many=True, read_only=True, context=self.context).data
        return variants


class BuilderSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Builder
        fields = ('name', )


class BuildHistorySerialiser(serializers.ModelSerializer):
    builder_name = BuilderSerialiser(read_only=True)

    class Meta:
        model = BuildHistory
        fields = ('builder_name', 'build_id', 'status', 'time_start', 'time_elapsed', 'watcher_id')


class PortListSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Port
        fields = ('name', )
