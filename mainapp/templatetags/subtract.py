from django import template

register = template.Library()

def subtract(value, arg):
    return value - int(arg)

register.filter('subtract', subtract)
