from django import template

from django.urls import reverse
from django.conf import settings

from ..models import Order

from liqpay import LiqPay

register = template.Library()

def create_payment_form(order_id):
    order = Order.objects.get(id=order_id)

    liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)
    params = {
        'action': 'pay',
        'amount': f'{order.cart.total_price}',
        'currency': 'UAH',
        'description': 'Оплата одежды',
        'order_id': f'{order.id}',
        'version': '3',
        'result_url': f'https://{settings.SHOP_DOMAIN_NAME}{reverse("client_orders")}',
        'server_url': f'https://{settings.SHOP_DOMAIN_NAME}{reverse("payment_result")}', # url to callback view
    }
    payment_form = liqpay.cnb_form(params)
    return payment_form

register.filter('create_payment_form', create_payment_form)
