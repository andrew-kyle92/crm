from django import template
from django.urls import reverse_lazy

import re

register = template.Library()


@register.filter(name='get_type')
def get_type(value):
    return type(value).__name__


@register.filter(name='current_url')
def current_url(value, arg=None):
    if arg:
        arg_url = reverse_lazy(arg)
        if arg_url == value:
            return True
        else:
            return False
    else:
        return False


@register.filter(name='get_street_adr_str')
def get_street_adr_str(value):
    street_adr_str = ''
    street_adr_str += value.street_address.replace(" ", "+")
    if value.street_address_2 is not None:
        street_adr_str += ",+" + value.street_address_2.replace(" ", "+")
    street_adr_str += ",+" + value.city.replace(" ", "+")
    street_adr_str += "+" + value.state.replace(" ", "+")
    street_adr_str += "+" + value.zip_code.replace(" ", "+")
    return street_adr_str


@register.filter(name='unslugify')
def unslugify(value):
    return re.sub(f"([_|-])", " ", value)
