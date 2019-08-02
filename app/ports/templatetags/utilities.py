from django import template

register = template.Library()


@register.simple_tag
def find_count_for_version(distribution, version):
    for i in distribution:
        if i['version'] == version:
            return i['num']
    return 0
