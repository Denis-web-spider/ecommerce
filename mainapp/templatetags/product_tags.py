from django import template

register = template.Library()

def remove_code_from_product_title(title):
    words = title.split()
    new_title = ''
    for word in words:
        if not word[0].isdigit():
            new_title += word + ' '
    return new_title

def pretty_price(price):
    price = str(price)
    new_price = ''
    for index, number in enumerate(price[::-1]):
        if index % 3 == 0:
            new_price += f' {number}'
        else:
            new_price += number
    new_price = new_price[::-1]
    return new_price

register.filter('remove_code_from_product_title', remove_code_from_product_title)
register.filter('pretty_price', pretty_price)
