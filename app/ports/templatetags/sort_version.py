from distutils.version import LooseVersion

from django import template

register = template.Library()


@register.filter('sortversion')
def sortversion(distribution, key):
    return sorted(distribution, key=lambda x: LooseVersion("0.0.1") if x[key] == "" else LooseVersion("0.0.2") if x[key] == "none" else LooseVersion(x[key]))
