from django import template

register = template.Library()

@register.filter
def div(value, arg):
    try:
        return value / float(arg)
    except Exception:
        return ''

@register.filter
def mult(value, arg):
    try:
        return value * arg
    except Exception:
        return ''
