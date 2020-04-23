from django.contrib import admin

from port.models import Port, Dependency


@admin.register(Port)
class Port(admin.ModelAdmin):
    list_display = ("name", "version", "active", "replaced_by")


@admin.register(Dependency)
class Dependency(admin.ModelAdmin):
    list_display = ("port_name", "type")
