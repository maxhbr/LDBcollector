from django import template
import time
import os
from django.conf import settings

register = template.Library()

@register.simple_tag
def version_date():
    version_path = settings.VERSION_FILE_PATH
    if version_path:
        with open(version_path, 'r') as file:
            data = file.read().rstrip()
            return data
    return ""
