from django import template

register = template.Library()

def translate_status(value):
    values = {
        'new': 'Новый заказ',
        'in_processing': 'В обработке',
        'delivered': 'Доставлен',
        'completed': 'Завершен'
    }
    return values[value]

def status_color(value):
    values = {
        'new': '#FF834A',
        'in_processing': '#C442FB',
        'delivered': '#7FFF4A',
        'completed': '#13A800'
    }
    return values[value]

def translate_payment_method(value):
    values = {
        'liqpay': 'Приват 24, картой VISA / MASTERCARD (LiqPay)'
    }
    return values[value]

def translate_payment_status(value):
    values = {
        True: 'Оплачено',
        False: 'Не оплачено',
    }
    return values[value]

def payment_status_color(value):
    values = {
        True: '#3FCD00',
        False: '#DE0822',
    }
    return values[value]

register.filter('translate_status', translate_status)
register.filter('status_color', status_color)
register.filter('translate_payment_method', translate_payment_method)
register.filter('translate_payment_status', translate_payment_status)
register.filter('payment_status_color', payment_status_color)
