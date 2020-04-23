from django.contrib import admin

from maintainer.models import Maintainer


@admin.register(Maintainer)
class Maintainer(admin.ModelAdmin):
    list_display = ("github", "name", "domain")
