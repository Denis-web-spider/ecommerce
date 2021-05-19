from django.db import models

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

from mainapp.models import Product

User = get_user_model()

class Cart(models.Model):
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Пользователь')
    completed = models.BooleanField(default=False, verbose_name='Завершена')
    total_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='Общее количество товара в корзине')
    total_price = models.IntegerField(default=0, verbose_name='Общая стоимость корзины')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлена')

    def get_total_quantity_and_price(self):
        items = self.items.all()
        total_quantity = 0
        total_price = 0
        if items:
            for item in items:
                total_quantity += item.quantity
                total_price += item.total_price
        self.total_quantity = total_quantity
        self.total_price = total_price
        self.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.completed == True:
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
            if not self.order:
                self.cart.get_total_quantity_and_price()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.cart.get_total_quantity_and_price()

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

    def __str__(self):
        return f'{self.first_name} | {self.second_name} | {self.phone_number} | {self.email} | {self.status}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']
