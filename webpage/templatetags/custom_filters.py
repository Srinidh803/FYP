# webpage/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def split_by_comma(value):
    return [item.strip() for item in value.split(',')] if value else []
