from django.shortcuts import render
from django.views.generic import View
from django.utils import timezone

import csv

from .forms import CsvForm
from .models import Csv

from mainapp.models import (
    Category,
    SubCategory,
    Product,
    Image,

    SpecificationValue,

    ProductFeatures,
    ProductSpecification,

    ProductMeasurementsKeys,
    ProductMeasurements
)

import traceback

class CsvImportView(View):

    def get(self, request):
        if request.user.is_superuser:
            form = CsvForm()
            context = {
                'form': form
            }

            return render(request, 'csv_import.html', context)
        else:
            return render(request, 'home.html')

    def post(self, request):
        if request.user.is_superuser:
            form = CsvForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                obj = Csv.objects.get(activated=False)
                obj.activated = True
                obj.save()
                context = {
                    'form': CsvForm()
                }
                with open(obj.file_name.path, newline='', encoding='cp1251') as f:
                    reader = csv.DictReader(f, delimiter=';')
                    for row in reader:
                        category, created = Category.objects.get_or_create(title=row['Категория'])
                        if row['Подкатегория']:
                            subcategory_title = row['Подкатегория']
                        else:
                            subcategory_title = row['Категория']
                        subcategory, created = SubCategory.objects.get_or_create(category=category, title=subcategory_title)
                        try:
                            product, created = Product.objects.get_or_create(category=subcategory, title=row['Название'])
                        except TypeError:
                            product = Product(category=subcategory, title=row['Название'], description=row['Описание'], true_price=int(row['Цена']))
                            created = True
                        product.description = row['Описание']
                        product.true_price = int(row['Цена'])
                        product.updated_at = timezone.now()
                        product.in_stock = True
                        product.save()

                        if created:
                            image_urls = row['Изображения'].split(';')
                            for image_url in image_urls:
                                image = Image(product=product, image_url=image_url)
                                image.save()

                        self.save_specification('Длина рукава', row, product)
                        self.save_specification('Состав', row, product)
                        self.save_specification('Сезон', row, product)
                        self.save_specification('Стиль', row, product)
                        self.save_specification('Вырез', row, product)
                        self.save_specification('Декорирование', row, product)
                        self.save_specification('Фасон', row, product)
                        self.save_specification('Комментарий к замерам', row, product)
                        self.save_specification('Пол', row, product)
                        self.save_specification('Цвет', row, product)
                        self.save_specification('Размер', row, product)
                        self.save_specification('Особенности модели', row, product)
                        self.save_specification('Параметры модели', row, product)
                        self.save_specification('Размер на фото', row, product)
                        self.save_specification('Рост', row, product)
                        self.save_specification('Застежка', row, product)
                        self.save_specification('Принадлежность', row, product)
                        self.save_specification('Фасон платья', row, product)
                        self.save_specification('Длина', row, product)
                        self.save_specification('Воротник', row, product)
                        self.save_specification('Материал', row, product)
                        self.save_specification('Модель', row, product)
                        self.save_specification('Посадка', row, product)
                        self.save_specification('Особенности ткани', row, product)
                        self.save_specification('Фасон юбки', row, product)
                        self.save_specification('Бренд', row, product)
                        self.save_specification('Длина брюк', row, product)
                        self.save_specification('Материал подкладки', row, product)
                        self.save_specification('Пряжка', row, product)
                        self.save_specification('Предназначение', row, product)
                        self.save_specification('Юбка', row, product)
                        self.save_specification('Комплект', row, product)

                        self.save_measurement('Длина изделия', row, product)
                        self.save_measurement('Длина рукава (см)', row, product)
                        self.save_measurement('Полуобхват груди', row, product)
                        self.save_measurement('Полуобхват пояса', row, product)
                        self.save_measurement('Ширина плеч', row, product)
                        self.save_measurement('Полуобхват бёдер', row, product)
                        self.save_measurement('Полуобхват пояса в брюках', row, product)
                        self.save_measurement('Длина изделия (вверх)', row, product)
                        self.save_measurement('Длина изделия (низ)', row, product)
                        self.save_measurement('Полуобхват пояса в юбке', row, product)
                        self.save_measurement('Полуобхват пояса шорты', row, product)
                        self.save_measurement('Полуобхват бёдер кардигана', row, product)
                        self.save_measurement('Ширина', row, product)
                        self.save_measurement('Толщина', row, product)
                        self.save_measurement('Глубина', row, product)
                        self.save_measurement('Полуобхват груди жилета', row, product)
                        self.save_measurement('Полуобхват пояса жилета', row, product)
                        self.save_measurement('Ширина плеч жилета', row, product)
                        self.save_measurement('Длина жилета', row, product)
                        self.save_measurement('Полуобхват пояса кардигана', row, product)
                        self.save_measurement('Полуобхват груди кардигана', row, product)
                        self.save_measurement('Ширина плеч кардигана', row, product)
                        self.save_measurement('Длина изделия (сзади)', row, product)
                        self.save_measurement('Длина по стельке (обувь)', row, product)
                        self.save_measurement('Размер Обувь', row, product)
                        self.save_measurement('Материал верха', row, product)
                        self.save_measurement('Размер шапки', row, product)
                        self.save_measurement('Ширина шарфа', row, product)
                        self.save_measurement('Длина шарфа', row, product)
                        self.save_measurement('Длина ремня', row, product)

                self.check_in_stock(days=1)

                return render(request, 'csv_import.html', context)
            else:
                return render(request, 'csv_import.html', {'form': form})
        else:
            return render(request, 'home.html')

    def save_specification(self, specification_key, row, product):
        specification_value = row.get(specification_key, '')
        if specification_value:
            product_feature, created = ProductFeatures.objects.get_or_create(feature_key=specification_key, category=product.category)
            product_feature_value, created = SpecificationValue.objects.get_or_create(value=specification_value)
            product_specification, created = ProductSpecification.objects.get_or_create(product=product, feature_key=product_feature, feature_value=product_feature_value)

    def save_measurement(self, measurement_key, row, product):
        measurement_value = row.get(measurement_key, '')
        if measurement_value:
            product_measurement_key, created = ProductMeasurementsKeys.objects.get_or_create(measurement_key=measurement_key, category=product.category)
            product_measurement_value, created = SpecificationValue.objects.get_or_create(value=measurement_value)
            product_measurement, created = ProductMeasurements.objects.get_or_create(product=product, measurement_key=product_measurement_key, measurement_value=product_measurement_value)

    def check_in_stock(self, days=0, hours=0, minutes=0, seconds=0):
        now = timezone.now()

        hours = (days * 24) + hours
        minutes = (hours * 60) + minutes
        seconds = (minutes * 60) + seconds

        for product in Product.objects.all():
            delta = now - product.updated_at
            delta_hours = (delta.days * 24)
            delta_minutes = (delta_hours * 60)
            delta_seconds = (delta_minutes * 60) + delta.seconds
            if delta_seconds > seconds:
                product.in_stock = False
                product.save()
            else:
                product.in_stock = True
                product.save()
