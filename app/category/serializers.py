from rest_framework import serializers

from category.models import Category


class CategoriesListSerializer(serializers.HyperlinkedModelSerializer):
    ports_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('name', 'ports_count')

    def get_ports_count(self, obj):
        return obj.ports.all().count()


class CategoryHaystackSerializer(serializers.Serializer):
    name = serializers.CharField()
