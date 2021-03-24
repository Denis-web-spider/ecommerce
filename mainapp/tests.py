from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from django.core.files.uploadedfile import SimpleUploadedFile

from datetime import date

from .models import (
Category,
SubCategory,
Product,
Review,
Image,

ReturnLetter,
ReturnItem
)

from cart.models import Cart, CartItem

UserModel = get_user_model()

class MainAppModelsTests(TestCase):

    def setUp(self) -> None:
        self.user = UserModel.objects.create(email='test@email.com', phone_number='+380674278265')
        self.user.set_password('password')
        self.user.save()
        self.cart = Cart.objects.create(owner=self.user)
        self.category = Category.objects.create(title='куртка')
        self.subcategory = SubCategory.objects.create(category=self.category, title='куртка')
        self.product = Product.objects.create(
            category=self.subcategory,
            title='test_product_title',
            description='test_product_description',
            true_price=100,
        )
        self.image = Image.objects.create(product=self.product, image=SimpleUploadedFile('image.jpg', b'jlkjl', content_type='image/jpeg'))
        self.review = Review.objects.create(product=self.product, user=self.user, ratting=5, review='test_review')
        self.product_2 = Product.objects.create(
            category=self.subcategory,
            title='shirt',
            description='test_product_description_2',
            true_price=100,
        )
        self.image_2 = Image.objects.create(product=self.product_2, image=SimpleUploadedFile('image.jpg', b'jlkjl', content_type='image/jpeg'))

    def test_category_model(self):
        self.assertEqual(self.category.sub_categories().first(), self.subcategory)
        self.assertEqual(list(self.category.get_all_products().order_by('title')), list(Product.objects.filter(category__category=self.category).order_by('title')))
        self.assertEqual(self.category.get_slug('куртка'), 'kurtka')
        self.assertEqual(self.category.slug, 'kurtka')
        self.assertEqual(str(self.category), 'куртка')

    def test_subcategory_model(self):
        self.assertEqual(self.subcategory.slug, 'kurtka')
        self.assertEqual(self.subcategory.products_count(), 2)
        self.assertEqual(list(self.subcategory.get_all_products().order_by('title')), list(Product.objects.filter(category__category=self.category).order_by('title')))
        self.assertEqual(self.category.get_slug('куртка'), 'kurtka')
        self.assertEqual(str(self.subcategory), 'куртка')

    def test_product_model(self):
        self.assertEqual(str(self.product), 'test_product_title')
        self.assertEqual(self.product.image(), self.image.image)
        self.assertEqual(self.product.images().first(), self.image)

        new_user = UserModel.objects.create(email='test_2@email.com', phone_number='+38067 42 78265', password='password')
        new_review = Review.objects.create(product=self.product, user=new_user, ratting=4, review='test_review_2')

        self.assertEqual(self.product.rounded_ratting(), 4)
        self.assertEqual(self.product.get_related_products()[0], self.product_2)
        self.assertEqual(self.product.get_price_with_morga(), self.product.morga + 0.99)
        self.assertEqual(self.product.price, self.product.morga + 0.99)

class MainAppViewsTests(TestCase):

    def setUp(self) -> None:
        self.user = UserModel.objects.create(email='test@email.com', phone_number='+380674278265')
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
        self.review = Review.objects.create(product=self.product, user=self.user, ratting=5, review='test_review')
        self.product_2 = Product.objects.create(
            category=self.subcategory,
            title='shirt',
            description='test_product_description_2',
            true_price=100,
        )
        self.image_2 = Image.objects.create(product=self.product_2, image=SimpleUploadedFile('image.jpg', b'jlkjl', content_type='image/jpeg'))

    def test_home_page_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, self.category.title)
        self.assertContains(response, self.product.title)
        self.assertNotContains(response, self.product.description)

    def test_category_list_view(self):
        response = self.client.get(self.category.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'category_products.html')
        self.assertContains(response, self.category.title)
        self.assertContains(response, self.subcategory.title)
        self.assertContains(response, self.product.title)
        self.assertContains(response, self.product_2.title)
        self.assertNotContains(response, self.product.description)
        self.assertNotContains(response, self.product_2.description)

    def test_subcategory_list_view(self):
        response = self.client.get(self.subcategory.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'subcategory_products.html')
        self.assertContains(response, self.category.title)
        self.assertContains(response, self.subcategory.title)
        self.assertContains(response, self.product.title)
        self.assertContains(response, self.product_2.title)
        self.assertNotContains(response, self.product.description)
        self.assertNotContains(response, self.product_2.description)

    def test_search_view(self):
        response = self.client.get(reverse('search'), {'search_query': 'shirt'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search_products.html')
        self.assertContains(response, self.category.title)
        self.assertContains(response, self.product_2.title)
        self.assertNotContains(response, self.product.title)
        self.assertNotContains(response, self.product.description)
        self.assertNotContains(response, self.product_2.description)

    def test_product_detail_view(self):
        response = self.client.get(self.product.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product_detail.html')
        self.assertContains(response, self.product.title)
        self.assertContains(response, self.product.description)
        self.assertContains(response, self.review.review)
        self.assertContains(response, self.product_2.title)
        self.assertNotContains(response, self.product_2.description)

        response = self.client.post(self.product.get_absolute_url(), {'quantity': '1', 'size': 'test_size', 'color': 'test_color'})
        self.assertEqual(response.status_code, 302)

        self.client.login(username='test@email.com', password='password')
        response = self.client.post(self.product.get_absolute_url(), {'quantity': '1', 'size': 'test_size', 'color': 'test_color'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product_detail.html')

        CartItem.objects.create(cart=self.cart, product=self.product, size='test_size', color='test_color')
        self.cart_item = CartItem.objects.get(cart=self.cart, product=self.product)
        self.assertEqual(self.cart_item.quantity, 1)
        self.assertEqual(self.cart_item.size, 'test_size')
        self.assertEqual(self.cart_item.color, 'test_color')

    def test_delete_review_view(self):
        self.assertEqual(Review.objects.count(), 1)
        response = self.client.post(reverse('delete_review') + f'?redirect={self.product.get_absolute_url()}', {'review_id': self.review.id})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 1)

        self.client.login(username='test@email.com', password='password')
        response = self.client.post(reverse('delete_review') + f'?redirect={self.product.get_absolute_url()}', {'review_id': self.review.id})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 0)

    def test_review_view(self):
        Review.objects.all().delete()
        self.assertEqual(Review.objects.count(), 0)

        self.client.login(username='test@email.com', password='password')
        response = self.client.post(reverse('review') + f'?redirect={self.product.get_absolute_url()}', {'product_id': self.product.id, 'ratting': '5', 'review': 'test_review'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.get(product=self.product).ratting, 5)
        self.assertEqual(Review.objects.get(product=self.product).review, 'test_review')

        response = self.client.post(reverse('review') + f'?redirect={self.product.get_absolute_url()}', {'product_id': self.product.id, 'ratting': '4', 'review': 'test_review_edited', 'edit': 'True'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.get(product=self.product).ratting, 4)
        self.assertEqual(Review.objects.get(product=self.product).review, 'test_review_edited')

        response = self.client.post(reverse('review') + f'?redirect={self.product.get_absolute_url()}', {'product_id': self.product.id, 'ratting': '5', 'review': 'test_review'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.get(product=self.product).ratting, 4)
        self.assertEqual(Review.objects.get(product=self.product).review, 'test_review_edited')

    def test_shipping_policy_view(self):
        response = self.client.get(reverse('shipping_policy'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'information/shipping_policy.html')

    def test_return_policy_view(self):
        response = self.client.get(reverse('return_policy'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'information/return_policy.html')

    def test_payment_policy_view(self):
        response = self.client.get(reverse('payment_policy'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'information/payment_policy.html')

    def test_privacy_policy_view(self):
        response = self.client.get(reverse('privacy_policy'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'information/privacy_policy.html')

    def test_clothes_size_view(self):
        response = self.client.get(reverse('clothes_size'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'information/clothes_size.html')

    def test_return_letter_view(self):
        response = self.client.get(reverse('return_letter'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'information/return_letter.html')

        self.assertEqual(ReturnLetter.objects.count(), 0)
        self.assertEqual(ReturnItem.objects.count(), 0)
        response = self.client.post(reverse('return_letter'), {
            'first_name': 'test_first_name',
            'middle_name': 'test_middle_name',
            'last_name': 'test_last_name',
            'email': 'test@email.com',
            'phone_number': '+38067 42 78265',
            'receive_order_date': date(21, 3, 20),
            'order_number': '1',
            'bank_card_number': '1111 1111 1111 1111',
            'fml_card_owner': 'test_fml',
            'comment': 'test_comment',

            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-0-product_name': 'test_product_name',
            'form-0-quantity': '1',
            'form-0-total_price': '100',
            'form-0-return_reason': '5',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'information/return_letter.html')
        self.assertEqual(ReturnLetter.objects.count(), 1)
        self.assertEqual(ReturnItem.objects.count(), 1)

        return_letter = ReturnLetter.objects.first()
        return_item = ReturnItem.objects.get(return_letter=return_letter)

        self.assertEqual(return_letter.first_name, 'test_first_name')
        self.assertEqual(return_letter.middle_name, 'test_middle_name')
        self.assertEqual(return_letter.last_name, 'test_last_name')
        self.assertEqual(return_letter.email, 'test@email.com')
        self.assertEqual(return_letter.phone_number, '+38067 42 78265')
        self.assertEqual(return_letter.receive_order_date, date(21, 3, 20))
        self.assertEqual(return_letter.order_number, '1')
        self.assertEqual(return_letter.bank_card_number, '1111 1111 1111 1111')
        self.assertEqual(return_letter.fml_card_owner, 'test_fml')
        self.assertEqual(return_letter.comment, 'test_comment')

        self.assertEqual(return_item.product_name, 'test_product_name')
        self.assertEqual(return_item.quantity, 1)
        self.assertEqual(return_item.total_price, 100)
        self.assertEqual(return_item.return_reason, '5')
