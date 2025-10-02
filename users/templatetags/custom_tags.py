# users/templatetags/custom_tags.py
from django import template
from django.conf import settings

register = template.Library()

@register.filter
def get_media_url(path):
    return settings.MEDIA_URL + path
