from django import template


register = template.Library()


@register.filter
def get_value(d, k):
    if k in d:
        return d[k]
    return None