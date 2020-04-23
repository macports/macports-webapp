from django.contrib import admin

from build.models import Builder, BuildHistory


@admin.register(Builder)
class Builder(admin.ModelAdmin):
    list_display = ("name", "display_name")


@admin.register(BuildHistory)
class BuildHistory(admin.ModelAdmin):
    list_display = ("build_id", "port_name", "builder_name")
