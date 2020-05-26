from rest_framework import serializers

from maintainer.serializers import MaintainerSerializer
from variant.serializers import VariantSerializer
from port.models import Port


# Used by autocomplete search queries
class PortHaystackSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()


class PortSerializer(serializers.ModelSerializer):
    maintainers = MaintainerSerializer(read_only=True, many=True)
    variants = VariantSerializer(read_only=True, many=True)

    class Meta:
        model = Port
        fields = ('name',
                  'portdir',
                  'categories',
                  'maintainers',
                  'version',
                  'variants',
                  'license',
                  'platforms',
                  'epoch',
                  'replaced_by',
                  'homepage',
                  'description',
                  'long_description',
                  'active')
