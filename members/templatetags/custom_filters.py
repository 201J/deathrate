from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """Add a CSS class to a form field."""
    
    if hasattr(field, 'widget'):
        field.widget.attrs['class'] = css_class
    return field
