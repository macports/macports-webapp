from django.db.models import Func


class StringToArray(Func):
    template = "%(function)s(regexp_replace(%(expressions)s, '[^0-9.]', '','g'), '.')::int[]"
    function = 'string_to_array'
