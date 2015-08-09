from django import template
from django.template.defaultfilters import stringfilter

from ..models import Entry


register = template.Library()

@register.filter
@stringfilter
def split(string):    	
    return str(string).split(",")

@register.filter
@stringfilter
def trim(value):
    return value.strip()

@register.inclusion_tag('_entry_history.html')
def entry_history():
    entries = Entry.objects.all().order_by('-modified_at')[:5]
    return {'entries': entries} 
