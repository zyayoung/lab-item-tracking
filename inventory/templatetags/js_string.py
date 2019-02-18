from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape

register = template.Library()


@register.filter
@stringfilter
def js_string(value):
    return mark_safe(
        conditional_escape(
            value.replace('\\', '\\\\')
        )
        .replace('&#39;', '\\\'')
        .replace('&quot;', '\\\"')
        .replace('&lt;', '<')
        .replace('&gt;', '>')
        .replace('&amp;', '&')
    )


@register.filter
def a(value):
    return {'v': value}


@register.filter
def b(value):
    return value['v']
