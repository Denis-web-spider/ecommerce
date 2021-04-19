from django.urls import path

from .views import CartView, CheckoutView, ClientOrdersView, ClientOrderDetail, PaymentResultView

urlpatterns = [
    path('my_orders/', ClientOrdersView.as_view(), name='client_orders'),
    path('order_detail/', ClientOrderDetail.as_view(), name='client_order_detail'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('', CartView.as_view(), name='cart'),
    path('payment_result/', PaymentResultView.as_view(), name='payment_result')
]
