from django import template

register = template.Library()


@register.filter('sortversion')
def sortversion(distribution, key):
    return sorted(distribution, key=lambda x: ((0, ) if x[key] == "none" else tuple(int(i) for i in x[key].split("."))))
