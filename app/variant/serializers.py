from rest_framework import serializers

from variant.models import Variant


class VariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = ('variant', )


class VariantHaystackSerializer(serializers.Serializer):
    variant = serializers.CharField()
