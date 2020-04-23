from django.contrib import admin

from category.models import Category


@admin.register(Category)
class Category(admin.ModelAdmin):
    list_display = ("name",)
