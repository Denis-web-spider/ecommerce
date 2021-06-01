from django.contrib import admin

from django.utils.html import mark_safe

from .models import (
    Category,
    SubCategory,
    Product,
    Image,
    Review,

    SpecificationValue,

    ProductFeatures,
    ProductSpecification,

    ProductMeasurementsKeys,
    ProductMeasurements,

    ReturnLetter,
    ReturnItem
)

class ImageInline(admin.TabularInline):
    model = Image
    fields = ['image', 'image_url']
    readonly_fields = ['image', 'image_url']
    extra = 0

class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    readonly_fields = ['feature_key', 'feature_value']
    extra = 0

class ProductMeasurementsInline(admin.TabularInline):
    model = ProductMeasurements
    readonly_fields = ['measurement_key', 'measurement_value']
    extra = 0

class ReviewInline(admin.TabularInline):
    model = Review
    readonly_fields = ['created_at']
    extra = 0

class ProductAdmin(admin.ModelAdmin):

    list_display = ['category_category_title', 'category_title', 'title', 'price', 'margin', 'discount', 'ratting', 'sales_count', 'in_stock', 'image_icon', 'created_at', 'updated_at']
    list_display_links = ['category_category_title', 'category_title', 'title', 'price', 'margin', 'discount', 'ratting', 'sales_count', 'in_stock', 'image_icon', 'created_at', 'updated_at']
    search_fields = ['category__category__title', 'category__title', 'title', 'price', 'ratting']
    list_filter = ['category__category__title', 'in_stock', 'created_at', 'updated_at']
    autocomplete_fields = ['category']
    actions = ['set_max_discount']

    inlines = [
        ImageInline,
        ProductSpecificationInline,
        ProductMeasurementsInline,
        ReviewInline
    ]

    def image_icon(self, obj):
        try:
            return mark_safe(f'<img src="{obj.image().url}" style="wight: 80px; height: 80px;">')
        except:
            return ''
    image_icon.short_description = 'Изображение'

    def category_title(self, obj):
        return obj.category.title
    category_title.short_description = 'Подкатегория'

    def category_category_title(self, obj):
        return obj.category.category.title
    category_category_title.short_description = 'Категория'

    @admin.action(description='Установить максимальную скидку')
    def set_max_discount(self, request, queryset):
        for target_product in queryset:
            the_same_product_in_all_categories = Product.objects.filter(title=target_product.title)
            for product in the_same_product_in_all_categories:
                product.discount = 100
                product.save()

class ProductFeaturesInline(admin.TabularInline):
    model = ProductFeatures

class ProductMeasurementsKeysInline(admin.TabularInline):
    model = ProductMeasurementsKeys

class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['category_title', 'title', 'slug']
    list_display_links = ['category_title', 'title', 'slug']
    search_fields = ['category__title', 'title', 'slug']

    inlines = [
        ProductFeaturesInline,
        ProductMeasurementsKeysInline
    ]

    def category_title(self, obj):
        return obj.category.title
    category_title.short_description = 'Категория'

class ReturnItemInline(admin.TabularInline):
    model = ReturnItem
    fields = ['product_name', 'quantity', 'total_price', 'return_reason']
    readonly_fields = ['return_reason']

class ReturnLetterAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'order_number', 'completed', 'created_at']
    list_display_links = ['full_name', 'email', 'order_number', 'completed', 'created_at']
    search_fields = ['first_name', 'middle_name', 'last_name', 'email', 'phone_number', 'order_number']
    list_filter = ['completed', 'created_at']
    inlines = [ReturnItemInline]

    def full_name(self, obj):
        return f'{obj.last_name} {obj.first_name} {obj.middle_name}'
    full_name.short_description = 'ФИО'

class SubCategoryInline(admin.TabularInline):
    model = SubCategory

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    list_display_links = ['title', 'slug']
    search_fields = ['title', 'slug']
    inlines = [SubCategoryInline]

class ImageAdmin(admin.ModelAdmin):
    list_display = ['product_title', 'image_url']
    list_display_links = ['product_title', 'image_url']
    search_fields = ['product__title']

    def product_title(self, obj):
        return obj.product.title
    product_title.short_description = 'Наименование товара'

class ProductFeaturesAdmin(admin.ModelAdmin):
    list_display = ['category_title', 'subcategory_title', 'feature_key']
    list_display_links = ['category_title', 'subcategory_title', 'feature_key']
    search_fields = ['category__title', 'category__category__title', 'feature_key']

    def category_title(self, obj):
        return obj.category.category.title
    category_title.short_description = 'Категория'

    def subcategory_title(self, obj):
        return obj.category.title
    subcategory_title.short_description = 'Подкатегория'

class ProductMeasurementsKeysAdmin(admin.ModelAdmin):
    list_display = ['category_title', 'subcategory_title', 'measurement_key']
    list_display_links = ['category_title', 'subcategory_title', 'measurement_key']
    search_fields = ['category__title', 'category__category__title', 'measurement_key']

    def category_title(self, obj):
        return obj.category.category.title
    category_title.short_description = 'Категория'

    def subcategory_title(self, obj):
        return obj.category.title
    subcategory_title.short_description = 'Подкатегория'

class ProductMeasurementsAdmin(admin.ModelAdmin):
    list_display = ['category_title', 'subcategory_title', 'measurement_key_value', 'measurement_value_value']
    list_display_links = ['category_title', 'subcategory_title', 'measurement_key_value', 'measurement_value_value']
    search_fields = ['product__category__title', 'product__category__category__title', 'measurement_key__measurement_key', 'measurement_value__value']

    def category_title(self, obj):
        return obj.product.category.category.title
    category_title.short_description = 'Категория'

    def subcategory_title(self, obj):
        return obj.product.category.title
    subcategory_title.short_description = 'Подкатегория'

    def measurement_key_value(self, obj):
        return obj.measurement_key.measurement_key
    measurement_key_value.short_description = 'Ключ измерения'

    def measurement_value_value(self, obj):
        return obj.measurement_value.value
    measurement_value_value.short_description = 'Значение измерения'

class ProductSpecificationAdmin(admin.ModelAdmin):
    list_display = ['category_title', 'subcategory_title', 'feature_key_value', 'feature_value_value']
    list_display_links = ['category_title', 'subcategory_title', 'feature_key_value', 'feature_value_value']
    search_fields = ['product__category__title', 'product__category__category__title', 'feature_key__feature_key', 'feature_value__value']

    def category_title(self, obj):
        return obj.product.category.category.title
    category_title.short_description = 'Категория'

    def subcategory_title(self, obj):
        return obj.product.category.title
    subcategory_title.short_description = 'Подкатегория'

    def feature_key_value(self, obj):
        return obj.feature_key.feature_key
    feature_key_value.short_description = 'Ключ характеристики'

    def feature_value_value(self, obj):
        return obj.feature_value.value
    feature_value_value.short_description = 'Значение характеристики'

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product_title', 'user', 'first_name', 'second_name', 'ratting', 'created_at']
    list_display_links = ['product_title', 'user', 'first_name', 'second_name', 'ratting', 'created_at']
    search_fields = ['product__title', 'user__email',  'first_name', 'second_name', 'ratting']
    list_filter = ['ratting', 'created_at']
    fields = ['product', 'user', 'first_name', 'second_name', 'ratting', 'review', 'created_at']
    readonly_fields = ['product', 'user', 'first_name', 'second_name', 'ratting', 'review', 'created_at']

    def product_title(self, obj):
        return obj.product.title
    product_title.short_description = 'Наименование товара'

class SpecificationValueAdmin(admin.ModelAdmin):
    list_display = ['value']
    list_display_links = ['value']
    search_fields = ['value']

admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Review, ReviewAdmin)

admin.site.register(ProductFeatures, ProductFeaturesAdmin)
admin.site.register(ProductSpecification, ProductSpecificationAdmin)

admin.site.register(ProductMeasurementsKeys, ProductMeasurementsKeysAdmin)
admin.site.register(ProductMeasurements, ProductMeasurementsAdmin)

admin.site.register(SpecificationValue, SpecificationValueAdmin)

admin.site.register(ReturnLetter, ReturnLetterAdmin)
