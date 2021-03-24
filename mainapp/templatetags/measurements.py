from django import template

register = template.Library()


def measurement_headers(string):
    """'L-65 см;XL-67 см;XXL-69 см;XXXL-71 см;4XL-73 см;' > [L, XL, XXL, XXXL, 4XL]"""
    if string:
        measurement_list = string.split(';')
        headers = []
        for unit in measurement_list:
            if unit.count('-') > 1:
                headers.append(unit.split('-')[0] + '-' + unit.split('-')[1])
            elif unit.count('-') == 0:
                return headers
            elif unit:
                headers.append(unit.split('-')[0])
        return headers
    else:
        return []

def measurement_values(string):
    """'L-65 см;XL-67 см;XXL-69 см;XXXL-71 см;4XL-73 см;' > [65 см, 67 см, 69 см, 71 см, 73 см]"""
    measurement_list = string.split(';')
    values = []
    for unit in measurement_list:
        if unit.count('-') > 1:
            values.append(unit.split('-')[2])
        elif unit:
            try:
                values.append(unit.split('-')[1])
            except:
                return measurement_list
    return values

register.filter('measurement_headers', measurement_headers)
register.filter('measurement_values', measurement_values)
