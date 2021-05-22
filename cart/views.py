from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage
from django.conf import settings

from django.views.generic import View

from .models import Cart, Order
from .forms import OrderForm
from .mails import (
    send_checkout_mail,
    send_payment_result_mail,
)

from liqpay import LiqPay
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


def get_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(owner=request.user, completed=False)
    else:
        return None
    return cart

class CartView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')

    def get(self, request):
        context = {}

        cart = get_cart(request)
        items = cart.items.all().order_by('product__title', 'size')

        context['items'] = items
        context['cart'] = cart

        return render(request, 'cart.html', context)

class CheckoutView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')

    def get(self, request):
        context = {}

        cart = get_cart(request)
        items = cart.items.all().order_by('product__title', 'size')
        form = OrderForm()

        context['items'] = items
        context['cart'] = cart
        context['form'] = form

        return render(request, 'checkout.html', context)

    def post(self, request):
        context = {}

        cart = get_cart(request)
        items = cart.items.all().order_by('product__title', 'size')

        form = OrderForm(request.POST)

        context['items'] = items
        context['cart'] = cart
        context['form'] = form

        if form.is_valid():
            order = Order.objects.create(
                cart=cart,
                first_name=form.cleaned_data['first_name'],
                middle_name=form.cleaned_data['middle_name'],
                second_name=form.cleaned_data['second_name'],
                phone_number=form.cleaned_data['phone_number'],
                email=form.cleaned_data['email'],
                region=form.cleaned_data['region'],
                locality=form.cleaned_data['locality'],
                post_office=form.cleaned_data['post_office'],
                payment_method=form.cleaned_data['payment_method'],
                comment=form.cleaned_data.get('comment', ''),
            )
            cart.completed = True
            cart.save()

            order = Order.objects.get(id=order.id)
            # в модели Order order.number меняется при помощи метода Queryset.update(number=10000 + self.id)
            # если не сделать так, то в письме клиенту прийдет номер заказа 10000
            # (Queryset.update(number=10000 + self.id) не успеет обновить order.number)

            send_checkout_mail(order)

            return HttpResponseRedirect(reverse('client_order_detail') + f'?order_id={order.id}')
        return render(request, 'checkout.html', context)

class ClientOrdersView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')

    def get(self, request):
        context = {}

        user = request.user
        cart = get_cart(request)
        orders = Order.objects.filter(cart__owner=user)

        paginator = Paginator(orders, 15)
        page_number = int(request.GET.get('page', 1))
        try:
            page_orders = paginator.page(page_number)
        except EmptyPage:
            page_orders = paginator.page(1)
        if page_number - 6 >= 0:
            page_range = list(paginator.page_range)[page_number - 6:page_number + 5]
            if len(page_range) < 11:
                index = 11 - len(page_range)
                page_range = list(paginator.page_range)[page_number - 6 - index:page_number + 5]
        else:
            page_range = list(paginator.page_range)[:page_number + 9]

        context['orders'] = page_orders
        context['page_range'] = page_range
        context['cart'] = cart

        return render(request, 'client_orders.html', context)

class ClientOrderDetail(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')

    def get(self, request):
        context = {}

        cart = get_cart(request)
        order_id = request.GET['order_id']
        order = Order.objects.get(id=order_id)

        context['order'] = order
        context['cart'] = cart

        return render(request, 'client_order_detail.html', context)

@method_decorator(csrf_exempt, name='dispatch')
class PaymentResultView(View):

    def post(self, request):
        liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)
        data = request.POST.get('data')
        signature = request.POST.get('signature')
        sign = liqpay.str_to_sign(settings.LIQPAY_PRIVATE_KEY + data + settings.LIQPAY_PRIVATE_KEY)
        if sign == signature:
            response = liqpay.decode_data_from_str(data)
            order = Order.objects.get(id=response['order_id'])
            response_status = response['status']
            if response_status == 'success':
                order.payment_status = True
                order.save()
                send_payment_result_mail(order, 'success')
            if response_status == 'error':
                send_payment_result_mail(order, 'error')
            if response_status == 'failure':
                send_payment_result_mail(order, 'failure')
            if response_status == 'reversed':
                send_payment_result_mail(order, 'reversed')
        return HttpResponse()
