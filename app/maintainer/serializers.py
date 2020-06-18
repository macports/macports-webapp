from rest_framework import serializers

from maintainer.models import Maintainer


class MaintainerListSerializer(serializers.ModelSerializer):
    ports_count = serializers.SerializerMethodField()

    class Meta:
        model = Maintainer
        fields = ('name', 'github', 'ports_count')

    def get_ports_count(self, obj):
        return obj.ports.all().count()


class MaintainerDetailSerializer(serializers.ModelSerializer):
    ports_count = serializers.SerializerMethodField()
    ports = serializers.SerializerMethodField()

    class Meta:
        model = Maintainer
        fields = ('name', 'github', 'ports_count', 'ports')

    def get_ports_count(self, obj):
        return obj.ports.all().count()

    def get_ports(self, obj):
        return obj.ports.filter(active=True).all().values_list('name', flat=True)


class MaintainerHaystackSerializer(serializers.Serializer):
    github = serializers.CharField()
