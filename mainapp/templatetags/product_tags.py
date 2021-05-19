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

@register.simple_tag
def colors_count_representation(product):
    colors_word_representation = {
        '1': 'Цвет',
        '2': 'Цвета',
        '3': 'Цвета',
        '4': 'Цвета',
        '5': 'Цветов',
        '6': 'Цветов',
        '7': 'Цветов',
        '8': 'Цветов',
        '9': 'Цветов',
        '0': 'Цветов',
        '11': 'Цветов',
        '12': 'Цветов',
        '13': 'Цветов',
        '14': 'Цветов',
    }
    colors_count_str = str(len(product.color_specifications()))

    if colors_count_str in colors_word_representation:
        color_word = colors_word_representation[colors_count_str]
    else:
        color_word = colors_word_representation[colors_count_str[-1]]

    return f'{colors_count_str} {color_word}'

register.filter('remove_code_from_product_title', remove_code_from_product_title)
register.filter('pretty_price', pretty_price)
