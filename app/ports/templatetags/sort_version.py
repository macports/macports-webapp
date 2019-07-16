from django import template

register = template.Library()


@register.filter('sortxcode')
def sort_xcode(xcode_distribution):
    return sorted(xcode_distribution, key=lambda x: ((0, ) if x['xcode_version'] == "none" else tuple(int(i) for i in x['xcode_version'].split("."))))
