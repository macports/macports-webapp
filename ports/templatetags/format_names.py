from django import template

register = template.Library()


@register.filter('os_version')
def trim_builder_name(builder_name):
    return builder_name.strip('x86_64')
