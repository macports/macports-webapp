from django.db import models


class Category(models.Model):
    name = models.TextField(primary_key=True, verbose_name="Name of the category")

    def __str__(self):
        return "%s" % self.name

    class Meta:
        db_table = "category"
        verbose_name = "Category"
        verbose_name_plural = "categories"
