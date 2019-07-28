from django import template
import itertools

register = template.Library()


@register.filter('unique_pairs')
def unique_pairs(distribution, keys):
    key1 = keys.split(' ')[0]
    key2 = keys.split(' ')[1]
    list_of_pairs = []
    for i in distribution:
        temp_list = [i[key1], i[key2]]
        if temp_list not in list_of_pairs:
            list_of_pairs.append(temp_list)
    return list_of_pairs
