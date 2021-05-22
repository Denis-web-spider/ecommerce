from django.template.loader import get_template
from django.core.mail import send_mail
from django.conf import settings

from mainapp.templatetags.product_tags import pretty_price

def send_checkout_mail(order):
    mail_context = {'order': order}

    text_mail_template = get_template('mails/checkout_mails/checkout_mail.txt')
    html_mail_template = get_template('mails/checkout_mails/checkout_mail.html')

    text_mail = text_mail_template.render(mail_context)
    html_mail = html_mail_template.render(mail_context)

    send_mail(
        subject=f'На сайте сделали заказ на {pretty_price(order.cart.total_price)} грн.',
        from_email=None,
        recipient_list=[settings.ADMIN_EMAIL],
        message=text_mail,
        html_message=html_mail
    )
    send_mail(
        subject=f'Вы совершили заказ на сайте DwsShop',
        from_email=None,
        recipient_list=[order.email],
        message=text_mail,
        html_message=html_mail
    )

def send_payment_result_mail(order, status):
    text_and_html_templates_for_payment_result = {
        'success': (
            'mails/payment_result_mails/payment_success_mail.txt',
            'mails/payment_result_mails/payment_success_mail.html'
        ),
        'error': (
            'mails/payment_result_mails/payment_error_mail.txt',
            'mails/payment_result_mails/payment_error_mail.html'
        ),
        'failure': (
            'mails/payment_result_mails/payment_failure_mail.txt',
            'mails/payment_result_mails/payment_failure_mail.html'
        ),
        'reversed': (
            'mails/payment_result_mails/payment_reversed_mail.txt',
            'mails/payment_result_mails/payment_reversed_mail.html'
        ),
    }

    mail_subjects_for_payment_result = {
        'success': 'Стату заказа изменён на "Оплачено".',
        'error': 'Неуспешный платеж. Некорректно заполнены данные.',
        'failure': 'Неуспешный платеж.',
        'reversed': 'Платеж возвращен.',
    }

    mail_context = {'order': order}

    text_mail_template = get_template(text_and_html_templates_for_payment_result[status][0])
    html_mail_template = get_template(text_and_html_templates_for_payment_result[status][1])

    text_mail = text_mail_template.render(mail_context)
    html_mail = html_mail_template.render(mail_context)

    send_mail(
        subject=mail_subjects_for_payment_result[status],
        from_email=None,
        recipient_list=[order.email],
        message=text_mail,
        html_message=html_mail
        )

def send_order_status_change_mail(order):

    mail_context = {'order': order}

    text_mail_template = get_template('mails/order_status_change_mails/general_status_change_mail.txt')
    html_mail_template = get_template('mails/order_status_change_mails/general_status_change_mail.html')

    text_mail = text_mail_template.render(mail_context)
    html_mail = html_mail_template.render(mail_context)

    send_mail(
        subject=f'Изменение статуса заказа №{pretty_price(order.number)}',
        from_email=None,
        recipient_list=[order.email],
        message=text_mail,
        html_message=html_mail
        )

def send_order_TTN_change_mail(order):
    mail_context = {'order': order}

    text_mail_template = get_template('mails/order_TTN_change_mails/order_TTN_change_mail.txt')
    html_mail_template = get_template('mails/order_TTN_change_mails/order_TTN_change_mail.html')

    text_mail = text_mail_template.render(mail_context)
    html_mail = html_mail_template.render(mail_context)

    send_mail(
        subject='Номер ТТН Новой Почты - интернет-магазин DwsShop',
        from_email=None,
        recipient_list=[order.email],
        message=text_mail,
        html_message=html_mail
        )
