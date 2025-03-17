from django import template

register = template.Library()


@register.filter
def can_create_kb(role):
    """Check if the role has permission to create knowledge bases"""
    return role in ["admin", "editor"]
