from django.db import models
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model

from django.core.files import File
from urllib.request import urlopen
from tempfile import NamedTemporaryFile

import uuid

import traceback
import requests

UserModel = get_user_model()

session = requests.Session()
adapter = requests.adapters.HTTPAdapter(
    max_retries=5
)

class Category(models.Model):
    title = models.CharField(max_length=255, verbose_name='Категория товара')
    slug = models.SlugField(unique=True)

    def sub_categories(self):
        return SubCategory.objects.filter(category=self)

    def get_absolute_url(self):
        return reverse('category_products', args=[self.slug])

    def get_all_products(self):
        return Product.objects.filter(category__category=self).order_by('-ratting').exclude(in_stock=False)

    def get_slug(self, russian_string):
        translate = {
            'а': 'a',
            'б': 'b',
            'в': 'v',
            'г': 'g',
            'д': 'd',
            'е': 'e',
            'ё': 'e',
            'ж': 'zh',
            'з': 'z',
            'и': 'i',
            'й': 'i',
            'к': 'k',
            'л': 'l',
            'м': 'm',
            'н': 'n',
            'о': 'o',
            'п': 'p',
            'р': 'r',
            'с': 's',
            'т': 't',
            'у': 'u',
            'ф': 'f',
            'х': 'kh',
            'ц': 'ts',
            'ч': 'ch',
            'ш': 'sh',
            'щ': 'shch',
            'ъ': 'ie',
            'ы': 'y',
            'ь': '',
            'э': 'e',
            'ю': 'iu',
            'я': 'ia'
        }
        russian_string = russian_string.lower().replace(' ', '-')
        new_string = ''
        for letter in russian_string:
            eng_letter = translate.get(letter, '-')
            new_string += eng_letter
        return new_string

    def save(self, *args, **kwargs):
        self.slug = self.get_slug(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория товара')
    title = models.CharField(max_length=255, verbose_name='Подкатегория товара')
    slug = models.SlugField(unique=False)

    def get_absolute_url(self):
        return reverse('subcategory_products', args=[self.category.slug, self.slug])

    def products_count(self):
        return Product.objects.filter(category=self).exclude(in_stock=False).count()

    def get_all_products(self):
        return self.product_set.all().order_by('-ratting').exclude(in_stock=False)

    def get_slug(self, russian_string):
        translate = {
            'а': 'a',
            'б': 'b',
            'в': 'v',
            'г': 'g',
            'д': 'd',
            'е': 'e',
            'ё': 'e',
            'ж': 'zh',
            'з': 'z',
            'и': 'i',
            'й': 'i',
            'к': 'k',
            'л': 'l',
            'м': 'm',
            'н': 'n',
            'о': 'o',
            'п': 'p',
            'р': 'r',
            'с': 's',
            'т': 't',
            'у': 'u',
            'ф': 'f',
            'х': 'kh',
            'ц': 'ts',
            'ч': 'ch',
            'ш': 'sh',
            'щ': 'shch',
            'ъ': 'ie',
            'ы': 'y',
            'ь': '',
            'э': 'e',
            'ю': 'iu',
            'я': 'ia'
        }
        russian_string = russian_string.lower().replace(' ', '-')
        new_string = ''
        for letter in russian_string:
            eng_letter = translate.get(letter, '-')
            new_string += eng_letter
        return new_string

    def save(self, *args, **kwargs):
        self.slug = self.get_slug(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(SubCategory, verbose_name='Подкатегория товара', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='Название товара')
    description = models.TextField(verbose_name='Описание товара', blank=True)
    morga = models.PositiveIntegerField(default=25, verbose_name='Моржа в %')
    true_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена на товар без моржы')
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена на товар')
    ratting = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)], verbose_name='Оценка')
    in_stock = models.BooleanField(verbose_name='В наличиии', default=True)
    created_at = models.DateTimeField(verbose_name='Создан', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Обновлён', blank=True, null=True)

    def __str__(self):
        return self.title

    def image(self):
        return Image.objects.filter(product=self).first().image

    def images(self):
        return Image.objects.filter(product=self)

    def images_for_category_list(self):
        return Image.objects.filter(product=self)[:3]

    def size_specifications(self):
        try:
            sizes = self.specifications.get(feature_key__feature_key='Размер').value().split(';')
        except ObjectDoesNotExist:
            sizes = None
        return sizes

    def color_specifications(self):
        try:
            colors = self.specifications.get(feature_key__feature_key='Цвет').value().split(';')
        except ObjectDoesNotExist:
            colors = None
        return colors

    def average_ratting(self):
        if self.reviews.all():
            list_of_reviews_ratings = []
            for review in self.reviews.all():
                list_of_reviews_ratings.append(review.ratting)
            self.ratting = sum(list_of_reviews_ratings)/len(list_of_reviews_ratings)
            self.save()
        else:
            self.ratting = 0
            self.save()

    def rounded_ratting(self):
        return round(self.ratting)

    def get_price_with_morga(self):
        return round(self.true_price / 100) * self.morga + round(self.true_price) + 0.99

    def get_related_products(self, count=10):
        products_with_four_star_or_greater = Product.objects.filter(category=self.category, ratting__gte=3.5).exclude(id=self.id).order_by('-ratting')[:count]
        remaining_product_count = count - products_with_four_star_or_greater.count()
        if remaining_product_count:
            return list(products_with_four_star_or_greater) + list(Product.objects.filter(category=self.category, ratting=0).exclude(id=self.id)[:remaining_product_count])
        else:
            return products_with_four_star_or_greater

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.category.category.slug, self.category.slug, str(self.id)])

    def save(self, *args, **kwargs):
        self.price = self.get_price_with_morga()
        super().save(*args, **kwargs)

class Review(models.Model):
    product = models.ForeignKey(Product, verbose_name='Продукт', related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(UserModel, verbose_name='Пользователь', on_delete=models.CASCADE)
    ratting = models.PositiveSmallIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)], verbose_name='Оценка')
    review = models.TextField(verbose_name='Отзыв')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.product} | {self.user} | {self.ratting}'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save()
        self.product.average_ratting()

    def delete(self, using=None, keep_parents=False):
        super().delete()
        self.product.average_ratting()

class Image(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    image = models.ImageField(upload_to='images', verbose_name='Изображение товара')
    image_url = models.URLField(verbose_name='Ссылка на изображение товара', blank=True)

    def save(self, *args, **kwargs):
        if self.image_url and not self.image:
            try:
                img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(session.get(self.image_url).content)
                img_temp.flush()
                self.image.save(f"image_{self.id}.jpeg", File(img_temp))
                super(Image, self).save(*args, **kwargs)
            except:
                traceback.print_exc()

    def __str__(self):
        return f'Изображение для {self.product.title}'

class SpecificationValue(models.Model):
    value = models.CharField(max_length=400, verbose_name='Значение характеристики')

    def __str__(self):
        return self.value

class ProductFeatures(models.Model):

    feature_key = models.CharField(max_length=50, verbose_name='Ключ характеристики')
    category = models.ForeignKey(SubCategory, verbose_name='Подкатегория', on_delete=models.CASCADE)

    def __str__(self):
        return f'"{self.category.category.title}" | "{self.category.title}" | "{self.feature_key}"'

class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, verbose_name='Продукт', on_delete=models.CASCADE, related_name='specifications')
    feature_key = models.ForeignKey(ProductFeatures, verbose_name='Ключ характеристики', on_delete=models.CASCADE)
    feature_value = models.ForeignKey(SpecificationValue, verbose_name='Значение характеристики', on_delete=models.CASCADE)

    def __str__(self):
        return f'"{self.product.category.category.title}" | "{self.product.category.title}" | "{self.product.title}" | "{self.feature_key.feature_key}" | "{self.feature_value.value}"'

    def key(self):
        return self.feature_key.feature_key

    def value(self):
        return self.feature_value.value

class ProductMeasurementsKeys(models.Model):

    measurement_key = models.CharField(max_length=50, verbose_name='Ключ измерения')
    category = models.ForeignKey(SubCategory, verbose_name='Подкатегория', on_delete=models.CASCADE)

    def __str__(self):
        return f'"{self.category.category.title}" | "{self.category.title}" | "{self.measurement_key}"'

class ProductMeasurements(models.Model):
    product = models.ForeignKey(Product, verbose_name='Продукт', on_delete=models.CASCADE, related_name='measurements')
    measurement_key = models.ForeignKey(ProductMeasurementsKeys, verbose_name='Ключ измерения', on_delete=models.CASCADE)
    measurement_value = models.ForeignKey(SpecificationValue, verbose_name='Значение измерения', on_delete=models.CASCADE)

    def __str__(self):
        return f'"{self.product.category.category.title}" | "{self.product.category.title}" | "{self.product.title}" | "{self.measurement_key.measurement_key}" | "{self.measurement_value.value}"'

    def key(self):
        return self.measurement_key.measurement_key

    def value(self):
        return self.measurement_value.value

class ReturnLetter(models.Model):

    first_name = models.CharField(max_length=255, verbose_name='Имя')
    middle_name = models.CharField(max_length=255, verbose_name='Отчество')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    email = models.EmailField(verbose_name='Электронная почта')
    phone_number = models.CharField(max_length=20, verbose_name='Номер телефона')
    receive_order_date = models.DateField(verbose_name='Дата получения товара ')
    order_number = models.CharField(max_length=50, verbose_name='№ заказа (или номер ТТН «Новой Почты»)')
    bank_card_number = models.CharField(max_length=50, verbose_name='Номер банковской карты')
    fml_card_owner = models.CharField(max_length=255, verbose_name='ФИО владельца карты')
    completed = models.BooleanField(default=False, verbose_name='Возврат завершен')
    comment = models.TextField(null=True, blank=True, verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.email} | {self.created_at} | {self.completed}'

class ReturnItem(models.Model):

    REASON_CHOICES = [
        ('1', 'Не подошел по размеру.'),
        ('2', 'Не подошел по внешнему виду.'),
        ('3', 'Товар не соответствует заказу.'),
        ('4', 'Брак.'),
        ('5', 'Другая причина (пожалуйста, укажите, какая именно)'),
    ]

    return_letter = models.ForeignKey(ReturnLetter, on_delete=models.CASCADE, related_name='items', verbose_name='Заявление на возврат товара')
    product_name = models.CharField(max_length=255, verbose_name='Название товара')
    quantity = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='Количество товара')
    total_price = models.DecimalField(max_digits=9, decimal_places=2, validators=[MinValueValidator(1)], verbose_name='Общая стоимость товара')
    return_reason = models.CharField(max_length=1, choices=REASON_CHOICES, verbose_name='Код причины возвращения')

    def __str__(self):
        return f'{self.return_letter.id} | {self.product_name} | {self.return_reason}'
