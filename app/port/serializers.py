from rest_framework import serializers


# SearchSerializer is used by PortSearchView to serialize results
# obtained from django-haystack
class SearchSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    maintainers = serializers.ListField()
    variants = serializers.ListField()
