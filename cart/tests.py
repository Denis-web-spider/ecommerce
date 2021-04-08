from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Cart, CartItem, Order
from mainapp.models import Category, SubCategory, Product, Image

from decimal import Decimal

UserModel = get_user_model()

class CartViewTests(TestCase):

    def setUp(self) -> None:
        self.user = UserModel.objects.create(email='test@email.com')
        self.user.set_password('password')
        self.user.save()
        self.cart = Cart.objects.create(owner=self.user)
        self.category = Category.objects.create(title='test_category_title', slug='test_category_slug')
        self.subcategory = SubCategory.objects.create(category=self.category, title='test_subcategory_title', slug='test_subcategory_slug')
        self.product = Product.objects.create(
            category=self.subcategory,
            title='test_product_title',
            description='test_product_description',
            true_price=100,
        )
        self.image = Image.objects.create(product=self.product, image=SimpleUploadedFile('image.jpg', b'jlkjl', content_type='image/jpeg'))
        self.cart_item = CartItem.objects.create(cart=self.cart, product=self.product, size='test_size', color='test_color')

    def test_cart_view(self):
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 302)

        self.client.login(username='test@email.com', password='password')
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart.html')
        self.assertContains(response, self.cart_item.size)
        self.assertContains(response, self.cart_item.color)
        self.assertContains(response, self.cart_item.quantity)

        response = self.client.post(reverse('cart'), {f'quantity_{self.cart_item.id}': '2'})
        self.assertEqual(response.status_code, 302)
        item = CartItem.objects.first()
        self.assertEqual(item.quantity, 2)

    def test_cart_item_delete_view(self):
        self.assertEqual(CartItem.objects.count(), 1)
        response = self.client.post(reverse('delete_cart_item'), {'item_id': self.cart_item.id})
        self.assertRedirects(response, reverse('login') + f'?next={reverse("delete_cart_item")}')

        self.client.login(username='test@email.com', password='password')
        response = self.client.post(reverse('delete_cart_item'), {'item_id': self.cart_item.id})
        self.assertRedirects(response, reverse('cart'))
        self.assertEqual(CartItem.objects.count(), 0)

    def test_checkout_view(self):
        response = self.client.get(reverse('checkout'))
        self.assertRedirects(response, reverse('login') + f'?next={reverse("checkout")}')

        self.client.login(username='test@email.com', password='password')
        response = self.client.get(reverse('checkout'))
        self.assertTemplateUsed(response, 'checkout.html')
        self.assertContains(response, self.cart_item.size)
        self.assertContains(response, self.cart_item.color)
        self.assertContains(response, self.cart_item.quantity)

        response = self.client.post(reverse('checkout'), {
            'first_name': 'test_first_name',
            'middle_name': 'test_middle_name',
            'second_name': 'test_second_name',
            'phone_number': '+38067 42 78265',
            'email': 'test@email.com',
            'region': 'test_region',
            'locality': 'test_locality',
            'post_office': 'test_post_office',
            'payment_method': 'liqpay'
        })
        self.assertRedirects(response, reverse('client_orders'))
        self.assertEqual(Order.objects.count(), 1)
        cart = Cart.objects.get(id=self.cart.id)
        cart_item = CartItem.objects.get(id=self.cart_item.id)
        order = Order.objects.get(cart=cart)

        self.assertTrue(cart.completed)
        self.assertEqual(cart_item.cart, self.cart)
        self.assertEqual(cart_item.order, order)
        self.assertEqual(cart_item.product, self.product)
        self.assertEqual(cart_item.quantity, 1)
        self.assertEqual(cart_item.size, 'test_size')
        self.assertEqual(cart_item.color, 'test_color')
        self.assertEqual(cart_item.total_price, Decimal(str(self.product.price)))

        self.assertEqual(order.cart, self.cart)
        self.assertEqual(order.first_name, 'test_first_name')
        self.assertEqual(order.middle_name, 'test_middle_name')
        self.assertEqual(order.second_name, 'test_second_name')
        self.assertEqual(order.phone_number, '+38067 42 78265')
        self.assertEqual(order.email, 'test@email.com')
        self.assertEqual(order.region, 'test_region')
        self.assertEqual(order.locality, 'test_locality')
        self.assertEqual(order.post_office, 'test_post_office')
        self.assertEqual(order.payment_method, 'liqpay')

    def test_client_orders_view(self):
        order = Order.objects.create(
            cart=self.cart,
            first_name='test_first_name',
            middle_name='test_middle_name',
            second_name='test_second_name',
            phone_number='+38067 42 78265',
            email='test@email.com',
            region='test_region',
            locality='test_locality',
            post_office='test_post_office',
        )

        response = self.client.get(reverse('client_orders'))
        self.assertRedirects(response, reverse('login') + f'?next={reverse("client_orders")}')

        self.client.login(username='test@email.com', password='password')
        response = self.client.get(reverse('client_orders'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'client_orders.html')
        self.assertContains(response, 'test_first_name')
        self.assertContains(response, 'test_middle_name')
        self.assertContains(response, 'test_second_name')
        self.assertContains(response, '+38067 42 78265')
        self.assertContains(response, 'test@email.com')
        self.assertContains(response, 'test_region')
        self.assertContains(response, 'test_locality')
        self.assertContains(response, 'test_post_office')

    def test_client_order_detail_view(self):
        order = Order.objects.create(
            cart=self.cart,
            first_name='test_first_name',
            middle_name='test_middle_name',
            second_name='test_second_name',
            phone_number='+38067 42 78265',
            email='test@email.com',
            region='test_region',
            locality='test_locality',
            post_office='test_post_office',
        )

        response = self.client.get(reverse('client_order_detail'))
        self.assertRedirects(response, reverse('login') + f'?next={reverse("client_order_detail")}')

        self.client.login(username='test@email.com', password='password')
        response = self.client.get(reverse('client_order_detail') + f'?order_id={order.id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'client_order_detail.html')
        self.assertContains(response, 'test_first_name')
        self.assertContains(response, 'test_middle_name')
        self.assertContains(response, 'test_second_name')
        self.assertContains(response, '+38067 42 78265')
        self.assertContains(response, 'test@email.com')
        self.assertContains(response, 'test_region')
        self.assertContains(response, 'test_locality')
        self.assertContains(response, 'test_post_office')
