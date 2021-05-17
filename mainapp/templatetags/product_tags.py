from django import template

register = template.Library()

def remove_code_from_product_title(title):
    words = title.split()
    new_title = ''
    for word in words:
        if not word[0].isdigit():
            new_title += word + ' '
    return new_title

register.filter('remove_code_from_product_title', remove_code_from_product_title)
