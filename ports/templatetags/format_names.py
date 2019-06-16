from django import template

register = template.Library()


@register.filter('os_version')
def trim_builder_name(builder_name):
    return builder_name.replace('_x86_64', '')


@register.filter('split')
def split(value, key):
    # Returns the value turned into a list.
    return value.split(key)


@register.filter('index')
def index(list, i):
    return list[int(i)]



