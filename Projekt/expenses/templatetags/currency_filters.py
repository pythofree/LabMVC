from django import template
from decimal import Decimal, ROUND_HALF_UP

register = template.Library()

@register.filter
def convert(amount, rate):
    """Convert PLN amount using given rate."""
    try:
        return (Decimal(str(amount)) / Decimal(str(rate))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    except Exception:
        return amount

@register.filter
def split(value, delimiter=','):
    return value.split(delimiter)
