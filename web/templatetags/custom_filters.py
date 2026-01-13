from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def replace_newline(value):
    """
    Replaces literal string '\n' with <br> tag
    """
    if isinstance(value, str):
        return mark_safe(value.replace('\\n', '<br>'))
    return value
