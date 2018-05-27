import re

from django import template
from django.urls import NoReverseMatch, reverse
from django.utils.translation import ugettext_lazy as _

register = template.Library()


@register.simple_tag(takes_context=True)
def active(context, pattern_or_urlname):
    try:
        pattern = "^" + reverse(pattern_or_urlname)
    except NoReverseMatch:
        pattern = pattern_or_urlname

    path = ""

    try:
        path = context["request"].path
    except KeyError:
        pass

    if re.search(pattern, path):
        return "active"
    return ""


@register.filter
def format_contract(contract):
    if contract is None:
        contract = _("None defined")
    return contract
