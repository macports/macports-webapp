from rest_framework import serializers

from maintainer.serializers import MaintainerSerializer
from variant.serializers import VariantSerializer
from port.models import Port


# SearchSerializer is used by PortSearchView to serialize results
# obtained from django-haystack
class SearchSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    maintainers = serializers.ListField()
    variants = serializers.ListField()


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
