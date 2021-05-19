from django.contrib import admin
from django.utils.html import format_html

from .models import Cart, CartItem, Order
from .templatetags.status import translate_status, status_color

class CartItemTabular(admin.StackedInline):
    model = CartItem

class CartItemTabularForOrderAdmin(CartItemTabular):
    readonly_fields = ['cart', 'product', 'total_price']
    fields = ['cart', 'product', 'quantity', 'size', 'color', 'total_price']
    extra = 0

class CartAdmin(admin.ModelAdmin):

    list_display = ['id', 'owner', 'total_quantity', 'total_price', 'completed']
    list_display_links = ['id', 'owner', 'total_quantity', 'total_price', 'completed']
    search_fields = ['owner.first_name', 'owner.last_name', 'total_quantity', 'total_price', 'completed']
    list_filter = ['completed', 'created_at']
    inlines = [CartItemTabularForOrderAdmin]

class OrderAdmin(admin.ModelAdmin):

    list_display = ['id', 'full_name', 'colored_status', 'payment_status', 'payment_method', 'created_at']
    list_display_links = ['id', 'full_name', 'colored_status', 'created_at', 'payment_status', 'payment_method']
    list_filter = ['status', 'created_at', 'payment_status', 'payment_method']
    search_fields = ['first_name', 'middle_name', 'second_name', 'email']
    inlines = [CartItemTabularForOrderAdmin]
    fieldsets = (
        ('ФИО', {
            'fields': ('second_name', 'first_name', 'middle_name')
        }),
        ('Контакты', {
            'fields': ('phone_number', 'email')
        }),
        ('Новая почта', {
            'fields': ('region', 'locality', 'post_office')
        }),
        ('Оплата', {
            'fields': ('payment_method', 'payment_status')
        }),
        (None, {
            'fields': ('comment', 'status')
        }),
    )

    def full_name(self, obj):
        return obj.second_name + ' ' + obj.first_name + ' ' + obj.middle_name
    full_name.short_description = 'Полное имя'
    full_name.admin_order_field = 'second_name'

    def colored_status(self, obj):
        ru_status = translate_status(obj.status)
        color = status_color(obj.status)
        return format_html(f'<span style="color: {color};">{ru_status}</span>')
    colored_status.short_description = 'Статус заказа'

class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart_owner', 'product_title', 'quantity', 'size', 'color', 'price', 'total_price']
    list_display_links = ['cart_owner', 'product_title', 'quantity', 'size', 'color', 'price', 'total_price']
    search_fields = ['cart__owner__email', 'product__title', 'size', 'color']
    list_filter = ['updated_at']
    fields = ['cart', 'order', 'product', 'quantity', 'size', 'color', 'price', 'total_price']
    readonly_fields = ['cart', 'order', 'product']
    def cart_owner(self, obj):
        return obj.cart.owner.email
    cart_owner.short_description = 'Владелец корзины'

    def product_title(self, obj):
        return obj.product.title
    product_title.short_description = 'Наименование товара'

admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Order, OrderAdmin)
