from rest_framework import serializers

from ports.models import Port, Maintainer, Variant, BuildHistory, Builder


class DynamicFieldsSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            fields = fields.split(',')
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class MaintainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maintainer
        fields = ('name', 'domain', 'github')


class VariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = ('variant', )


class PortSerializer(DynamicFieldsSerializer):
    maintainers = MaintainerSerializer(read_only=True, many=True)
    variants = serializers.SerializerMethodField()

    class Meta:
        model = Port
        fields = ('name', 'portdir', 'categories', 'maintainers', 'version', 'revision', 'variants', 'platforms', 'homepage', 'epoch', 'description', 'long_description', 'active', 'replaced_by')

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
