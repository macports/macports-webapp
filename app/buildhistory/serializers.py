from rest_framework import serializers

from buildhistory.models import BuildHistory, Builder


class BuilderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Builder
        fields = ('name', 'display_name')


class BuildHistorySerializer(serializers.ModelSerializer):
    builder_name = BuilderSerializer(read_only=True)

    class Meta:
        model = BuildHistory
        fields = ('builder_name', 'build_id', 'status', 'time_start', 'time_elapsed', 'watcher_id')
