from rest_framework import serializers

from ports.models import Port, Maintainer, Variant, Category


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
