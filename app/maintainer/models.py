from django.db import models
from django.urls import reverse


class Maintainer(models.Model):
    name = models.CharField(max_length=50, default='')
    domain = models.CharField(max_length=50, default='')
    github = models.CharField(max_length=50, default='')
    ports = models.ManyToManyField('port.Port', related_name='maintainers')

    class Meta:
        db_table = "maintainer"
        verbose_name = "Maintainer"
        verbose_name_plural = "Maintainers"
        unique_together = [['name', 'domain', 'github']]
        indexes = [
            models.Index(fields=['github']),
            models.Index(fields=['name', 'domain'])
        ]

    def get_absolute_url_github(self):
        return reverse('maintainer_detail_github', args=[str(self.github)])

    def get_absolute_url_email(self):
        return reverse('maintainer_detail_email', args=[str(self.name), str(self.domain)])
