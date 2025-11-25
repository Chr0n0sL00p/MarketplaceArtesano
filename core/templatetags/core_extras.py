from django import template
import math

register = template.Library()

@register.filter(name='filter_by_type')
def filter_by_type(notificaciones, types):
    type_list = [t.strip() for t in types.split(',')]
    return [n for n in notificaciones if n.tipo in type_list]

@register.filter(name='eq')
def eq(value, arg):
    return value == arg

@register.filter(name='price')
def price(value):
    try:
        return '{:,.0f}'.format(value).replace(',', '.')
    except (ValueError, TypeError):
        return value
