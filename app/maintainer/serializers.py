from rest_framework import serializers

from maintainer.models import Maintainer


class MaintainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maintainer
        fields = ('name', 'domain', 'github')
