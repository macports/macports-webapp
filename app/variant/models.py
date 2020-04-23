from django.db import models


class Variant(models.Model):
    port = models.ForeignKey('port.Port', on_delete=models.CASCADE, related_name='ports')
    variant = models.CharField(max_length=100, default='')

    class Meta:
        db_table = "variant"
        verbose_name = "Variant"
        verbose_name_plural = "Variants"
