from rest_framework import serializers


class FollowedPortsSerializer(serializers.Serializer):
    usr = None
    ports = serializers.SerializerMethodField()

    def get_context(self):
        usr = self.context.get('user')
        return usr

    def get_ports(self, obj):
        usr = self.get_context()
        if not usr:
            return []

        return usr.ports.all().values_list('name', flat=True)
