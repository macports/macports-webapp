from django import template

register = template.Library()


@register.simple_tag
def find_count_for_version(distribution, version):
    for i in distribution:
        if i['version'] == version:
            return i['num']
    return 0


@register.simple_tag
def most_installed_version(distribution):
    sorted_dict = sorted(distribution, key=lambda x: x['num'], reverse=True)
    expression = "{} ({} users)".format(sorted_dict[0]['version'], sorted_dict[0]['num'])
    return expression
