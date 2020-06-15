from rest_framework import serializers

from category.models import Category


class CategoriesListSerializer(serializers.HyperlinkedModelSerializer):
    ports_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('name', 'ports_count')

    def get_ports_count(self, obj):
        return obj.ports.all().count()


class CategoryDetailSerializer(serializers.HyperlinkedModelSerializer):
    ports_count = serializers.SerializerMethodField()
    ports = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('name', 'ports_count', 'ports')

    def get_ports_count(self, obj):
        return obj.ports.all().filter(active=True).count()

    def get_ports(self, obj):
        return obj.ports.all().filter(active=True).values_list('name', flat=True)


class CategoryHaystackSerializer(serializers.Serializer):
    name = serializers.CharField()
