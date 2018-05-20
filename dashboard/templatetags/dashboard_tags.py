from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()


@register.filter(name='formatnumber')
def format_number(value, arg=0):
    try:
        rounded_value = round(float(value), arg)
        int_part = intcomma(int(rounded_value))
        if arg > 0:
            return "{0}{1}".format(int_part, ("%0.2f" % rounded_value)[-3:])
        else:
            return int_part
    except:
        return value


@register.filter(name='formattimediff')
def format_timediff(value, arg=''):
    days, remainder = divmod(value.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    days = int(days)
    hours = int(hours)
    minutes = int(minutes)

    if days > 0:
        if arg == 'short':
            return "{0}d {1}h".format(days, hours)
        return "{0}d {1}h {2}min".format(days, hours, minutes)
    else:
        return "{0}h {1}min".format(hours, minutes)
