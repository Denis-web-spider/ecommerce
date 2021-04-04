from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage
from django.conf import settings
from django.core.mail import send_mail

from django.views.generic import View

from .models import Cart, Order
from .forms import OrderForm, SearchForm

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

    def post(self, request):
        cart = get_cart(request)
        items = cart.items.all()

        for item in items:
            quantity = self.validate_quantity(request, request.POST[f'quantity_{item.id}'])
            if quantity or quantity == 0:
                item.quantity = quantity
                item.save()

        return HttpResponseRedirect(reverse('cart'))

    def validate_quantity(self, request, quantity):
        try:
            quantity = int(quantity)
        except ValueError:
            messages.error(request, 'Некорректное значение в поле для количества товара')
            return False
        else:
            return quantity

class DeleteCartItemView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')

    def post(self, request):

        item_id = request.POST['item_id']

        cart = get_cart(request)
        product_title = cart.items.get(id=item_id).product.title
        cart.items.get(id=item_id).delete()

        messages.success(request, f'Товар {product_title} успешно удален из вашей корзины')

        return HttpResponseRedirect(reverse('cart'))

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
            order.save()
            cart.completed = True
            cart.save()

            message, html_message = self.get_message_and_html_message_for_email(order)
            send_mail(
                subject=f'На сайте сделали заказ на {order.cart.total_price}грн.',
                from_email=None,
                recipient_list=[settings.ADMIN_EMAIL],
                message=message,
                html_message=html_message
            )
            send_mail(
                subject=f'Вы совершили заказ на сайте',
                from_email=None,
                recipient_list=[order.email],
                message=message,
                html_message=html_message
            )

            return HttpResponseRedirect(reverse('client_order_detail') + f'?order_id={order.id}')
        return render(request, 'checkout.html', context)

    def get_message_and_html_message_for_email(self, order):
        '''Принимает order, возвращает (message, html_message)'''
        message = (
            f"""
            Номер заказа: {order.id}
            
            ФИО: {order.second_name} {order.first_name}
            
            Номер телефона: {order.phone_number}
            
            Электронная почта: {order.email}
            
            Новая почта:
            Область: {order.region}
            Населенный пункт: {order.locality}
            Отделение новой почты: {order.post_office}
            
            Комментарий {order.comment}
            """
        )
        html_message = (
            f"""
            <p>Номер заказа: {order.id}</p>
            <br>
            <p>ФИО: {order.second_name} {order.first_name}</p>
            <br>
            <p>Номер телефона: {order.phone_number}</p>
            <br>
            <p>Электронная почта: {order.email}</p>
            <br>
            <p>Новая почта:
            <p>Область: {order.region}</p>
            <p>Населенный пункт: {order.locality}</p>
            <p>Отделение новой почты: {order.post_office}</p>
            <br>
            <p>Комментарий {order.comment}</p>
            <br>
            <table class="table">
                <caption>Список товаров</caption>
                <thead>
                    <tr>
                        <th scope="col">№</th>
                        <th scope="col">Наименование</th>
                        <th scope="col">Кол-во, шт.</th>
                        <th scope="col">Размер</th>
                        <th scope="col">Цвет</th>
                        <th scope="col">Цена, грн.</th>
                    </tr>
                </thead>
                <tbody>
            """
        )
        for index, item in enumerate(order.cart.items.all()):
            item_number = index + 1
            message += f'\n{item.product.title} {item.quantity} {item.size} {item.color} {item.total_price}'
            html_message += (
                f"""
                <tr>
                    <td>{item_number}</td>
                    <td>{item.product.title}</td>
                    <td>{item.quantity}</td>
                    <td>{item.size}</td>
                    <td>{item.color}</td>
                    <td>{item.total_price}</td>
                </tr>
                """
            )

        message += f'\nВсего товара в корзине {order.cart.total_quantity}, общая сумма {order.cart.total_price}грн.'
        html_message += (
            f"""
                </tbody>
            </table>
            <br>
            <p>Всего товара в корзине {order.cart.total_quantity}, общая сумма {order.cart.total_price}грн.</p>
            """
        )
        return message, html_message

class ClientOrdersView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')

    def get(self, request):
        context = {}

        user = request.user
        cart = get_cart(request)
        orders = Order.objects.filter(cart__owner=user).order_by('-created_at')

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

        context['order'] = order
        context['cart'] = cart
        context['payment_form'] = payment_form

        return render(request, 'client_order_detail.html', context)

@method_decorator(csrf_exempt, name='dispatch')
class PaymentResultView(View):

    def post(self, request, *args, **kwargs):
        liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)
        data = request.POST.get('data')
        signature = request.POST.get('signature')
        sign = liqpay.str_to_sign(settings.LIQPAY_PRIVATE_KEY + data + settings.LIQPAY_PRIVATE_KEY)
        if sign == signature:
            print('==' * 100)
            print('callback is valid')
            print('==' * 100)
        response = liqpay.decode_data_from_str(data)
        print('==' * 100)
        print('callback data', response)
        print('==' * 100)
        return HttpResponse()
