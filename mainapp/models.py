from django.db import models
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model

from django.core.files import File
from tempfile import NamedTemporaryFile

import uuid

import traceback
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

UserModel = get_user_model()

session = requests.Session()
retries = Retry(total=5,
                backoff_factor=2,
                status_forcelist=[500, 502, 503, 504]
                )
session.mount('http://', HTTPAdapter(max_retries=retries))
session.mount('https://', HTTPAdapter(max_retries=retries))

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'no-cache',
    'Cookie': "_ga=GA1.2.1988127041.1614534506; _fbp=fb.1.1614534511008.1455577828; shipping_method=novaposhta.novaposhta; payment_method=liqpay; language=ru; currency=UAH; PHPSESSID=1hjcsnevtboifbaenm0r12hp07; _gid=GA1.2.1445165545.1617120854; biatv-cookie={%22firstVisitAt%22:1613420799%2C%22visitsCount%22:41%2C%22campaignCount%22:5%2C%22currentVisitStartedAt%22:1617120850%2C%22currentVisitLandingPage%22:%22https://timeofstyle.com/muzhskaya-odezhda-1/%22%2C%22currentVisitOpenPages%22:2%2C%22location%22:%22https://timeofstyle.com/futbolka-s-nadpisyu-na-grudi-85f395.html%22%2C%22userAgent%22:%22Mozilla/5.0%20(Windows%20NT%2010.0%3B%20Win64%3B%20x64)%20AppleWebKit/537.36%20(KHTML%2C%20like%20Gecko)%20Chrome/89.0.4389.90%20Safari/537.36%22%2C%22language%22:%22ru-ru%22%2C%22encoding%22:%22utf-8%22%2C%22screenResolution%22:%221536x864%22%2C%22currentVisitUpdatedAt%22:1617120875%2C%22utmDataCurrent%22:{%22utm_source%22:%22www.liqpay.ua%22%2C%22utm_medium%22:%22referral%22%2C%22utm_campaign%22:%22(referral)%22%2C%22utm_content%22:%22/%22%2C%22utm_term%22:%22(not%20set)%22%2C%22beginning_at%22:1615487167}%2C%22campaignTime%22:1615487167%2C%22utmDataFirst%22:{%22utm_source%22:%22google%22%2C%22utm_medium%22:%22organic%22%2C%22utm_campaign%22:%22(not%20set)%22%2C%22utm_content%22:%22(not%20set)%22%2C%22utm_term%22:%22(not%20provided)%22%2C%22beginning_at%22:1613420799}%2C%22geoipData%22:{%22country%22:%22Ukraine%22%2C%22region%22:%22Kirovohrads'ka%20Oblast'%22%2C%22city%22:%22Kirovograd%22%2C%22org%22:%22PJSC%20Ukrtelecom%22}}; __atuvc=7%7C9%2C9%7C10%2C6%7C11%2C1%7C12%2C1%7C13; __atuvs=60634e6c15eadcbd000; bingc-activity-data={%22numberOfImpressions%22:0%2C%22activeFormSinceLastDisplayed%22:0%2C%22pageviews%22:1%2C%22callWasMade%22:0%2C%22updatedAt%22:1617120901}",
    'DNT': '1',
    'Host': 'timeofstyle.com',
    'Pragma': 'no-cache',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
}

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
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    second_name = models.CharField(max_length=255, verbose_name='Фамилия')
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
                img_temp.write(session.get(self.image_url, headers=headers).content)
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
