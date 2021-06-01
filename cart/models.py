from django.db import models

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MinLengthValidator, MaxLengthValidator

from mainapp.models import Product

from .mails import send_order_status_change_mail, send_order_TTN_change_mail

import uuid

User = get_user_model()

class Cart(models.Model):
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Пользователь')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    completed = models.BooleanField(default=False, verbose_name='Завершена')
    total_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='Общее количество товара в корзине')
    total_price = models.IntegerField(default=0, verbose_name='Общая стоимость корзины')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлена')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.was_completed = False

    def save(self, *args, **kwargs):
        total_quantity = 0
        total_price = 0
        for item in self.items.all():
            total_quantity += item.quantity
            total_price += item.total_price
        self.total_quantity = total_quantity
        self.total_price = total_price
        super().save(*args, **kwargs)
        if (self.completed == True) and (self.completed != self.was_completed):
            self.was_completed = True
            order = Order.objects.get(cart=self)
            for item in self.items.all():
                item.order = order
                item.save()

    def __str__(self):
        return f'{self.id} | {self.total_price} | {self.total_price} | {self.created_at} | {self.updated_at}'

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        ordering = ['-id']

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, verbose_name='Корзина', related_name='items')
    order = models.ForeignKey('Order', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Заказ', related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукт')
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(0)], verbose_name='Количество товара')
    size = models.CharField(max_length=10, null=True, blank=True, verbose_name='Размер')
    color = models.CharField(max_length=100, null=True, blank=True, verbose_name='Цвет')
    price = models.IntegerField(verbose_name='Стоимость товара')
    total_price = models.IntegerField(default=0, verbose_name='Общая стоимость товара')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлена')

    def save(self, *args, **kwargs):
        self.price = self.product.price
        if self.quantity == 0:
            self.delete()
        else:
            self.total_price = self.price * self.quantity
            super().save(*args, **kwargs)
            self.cart.save()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.cart.save()

    def __str__(self):
        return f'{self.cart.id} | {self.product.title} | {self.quantity} | {self.total_price} | {self.created_at} | {self.updated_at}'

    class Meta:
        verbose_name = 'Продукт корзины'
        verbose_name_plural = 'Продукты корзины'
        ordering = ['-cart__id']

class Order(models.Model):
    NEW = 'new'
    IN_PROCESSING = 'in_processing'
    DELIVERED = 'delivered'
    COMPLETED = 'completed'

    STATUS_CHOICES = [
        (NEW, 'Новый заказ'),
        (IN_PROCESSING, 'В обработке'),
        (DELIVERED, 'Доставлен'),
        (COMPLETED, 'Завершен'),
    ]

    LiqPay = 'liqpay'

    PaymentMethod = [
        (LiqPay, 'Приват 24, картой VISA / MASTERCARD (LiqPay)'),
    ]

    number = models.IntegerField(default=10000, verbose_name='№')
    TTN = models.CharField(max_length=100, default='00000000000000', verbose_name='ТТН №', validators=[MinLengthValidator(14), MaxLengthValidator(14)])
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE, verbose_name='Корзина')
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    middle_name = models.CharField(max_length=100, verbose_name='Отчество')
    second_name = models.CharField(max_length=100, verbose_name='Фамилия')
    phone_number = models.CharField(max_length=20, verbose_name='Номер телефона')
    email = models.EmailField(verbose_name='Почта')
    region = models.CharField(max_length=100, verbose_name='Область')
    locality = models.CharField(max_length=100, verbose_name='Населенный пункт')
    post_office = models.CharField(max_length=200, verbose_name='Отделение новой почты')
    comment = models.TextField(verbose_name='Комментарий', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=NEW, verbose_name='Статус заказа')
    payment_method = models.CharField(max_length=20, choices=PaymentMethod, default=LiqPay, verbose_name='Способ оплаты')
    payment_status = models.BooleanField(default=False, verbose_name='Статус оплаты')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.latest_status = self.status
        self.latest_TTN = self.TTN

    def __str__(self):
        return f'{self.first_name} | {self.second_name} | {self.phone_number} | {self.email} | {self.status}'

    def set_order_number(self):
        Order.objects.filter(id=self.id).update(number=10000 + self.id)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.set_order_number()
        if self.latest_status != self.status:
            self.latest_status = self.status
            send_order_status_change_mail(self)
            if self.status == self.COMPLETED:
                for item in self.cart.items.all():
                    product = item.product
                    product.sales_count += item.quantity
                    product.save()
        if self.latest_TTN != self.TTN:
            self.latest_TTN = self.TTN
            send_order_TTN_change_mail(self)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']
