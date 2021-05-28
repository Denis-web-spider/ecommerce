from django.shortcuts import render, reverse, redirect
from django.views.generic import View
from django.contrib import messages
from django.conf import settings

from .models import Category, Product, SubCategory, ReturnLetter, ReturnItem
from .mixins import LeftSideBarMixin
from .forms import ProductForm, SearchForm, ReturnLetterForm, ReturnItemFormset
from .utils import (
    products_queryset_searched_sorted_and_filtered,
    products_pagination
)
from .mails import send_return_letter_mail_for_admin

from cart.cart import get_cart


class HomePageView(LeftSideBarMixin, View):

    def get(self, request):
        context = self.get_context_data()

        high_ratting_products_for_main_slider = []
        for category in Category.objects.all():
            products = tuple(category.get_all_products()[:2])
            if len(products) == 2:
                high_ratting_products_for_main_slider.append(products)

        side_products = Product.objects.all().order_by('-ratting').exclude(in_stock=False)[:5]
        most_popular_products = Product.objects.all().order_by('-ratting').exclude(in_stock=False)[:10]
        recent_products = Product.objects.filter(category__category__title='Новинки').order_by('-ratting').exclude(in_stock=False)[:10]
        cart = get_cart(request)

        context['high_ratting_products_for_main_slider'] = high_ratting_products_for_main_slider
        context['side_products'] = side_products
        context['most_popular_products'] = most_popular_products
        context['recent_products'] = recent_products
        context['cart'] = cart

        return render(request, 'home.html', context)

class CategoryProductsListView(LeftSideBarMixin, View):

    def get(self, request, slug):
        context = self.get_context_data()
        cart = get_cart(request)

        current_category = Category.objects.get(slug=slug)
        products = current_category.get_all_products()
        products = products_queryset_searched_sorted_and_filtered(products, request)
        page_obj, page_range = products_pagination(products, request)

        form = SearchForm(request.GET)
        form.populate_choice_fields()
        form.fields['title'].widget.attrs.update({'data-category': f'{current_category}'})

        context['slug'] = slug
        context['current_category'] = current_category
        context['products'] = page_obj
        context['products_total_count_from_search'] = products.count()
        context['page_range'] = page_range
        context['cart'] = cart
        context['form'] = form

        return render(request, 'category_products.html', context)

class SubcategoryProductsListView(LeftSideBarMixin, View):

    def get(self, request, category_slug, subcategory_slug):
        context = self.get_context_data()
        cart = get_cart(request)

        current_category = Category.objects.get(slug=category_slug)
        current_subcategory = SubCategory.objects.get(category=current_category, slug=subcategory_slug)
        products = current_subcategory.get_all_products()
        products = products_queryset_searched_sorted_and_filtered(products, request)
        page_obj, page_range = products_pagination(products, request)

        form = SearchForm(request.GET)
        form.populate_choice_fields()
        form.fields['title'].widget.attrs.update({'data-category': f'{current_category}',
                                                  'data-subcategory': f'{current_subcategory}'})

        context['slug'] = category_slug
        context['subcategory_slug'] = subcategory_slug
        context['current_category'] = current_category
        context['current_subcategory'] = current_subcategory
        context['products'] = page_obj
        context['products_total_count_from_search'] = products.count()
        context['page_range'] = page_range
        context['cart'] = cart
        context['form'] = form

        return render(request, 'subcategory_products.html', context)

class SearchView(LeftSideBarMixin, View):

    def get(self, request):
        context = self.get_context_data()
        cart = get_cart(request)
        search_query = request.GET['search_query']

        products = Product.objects.all().exclude(in_stock=False).order_by('-discount')
        products = products_queryset_searched_sorted_and_filtered(products, request)
        page_obj, page_range = products_pagination(products, request)

        form = SearchForm(request.GET)
        form.populate_choice_fields()
        form.fields['title'].widget.attrs.update({'data-search_query': f'{search_query}'})

        context['products'] = page_obj
        context['products_total_count_from_search'] = products.count()
        context['page_range'] = page_range
        context['cart'] = cart
        context['form'] = form
        context['search_query'] = search_query

        return render(request, 'search_products.html', context)

class ProductDetailView(View):

    def get(self, request, category_slug, subcategory_slug, id):
        context = {}
        current_category = Category.objects.get(slug=category_slug)
        current_subcategory = SubCategory.objects.get(category=current_category, slug=subcategory_slug)
        product = Product.objects.get(id=id)
        cart = get_cart(request)

        form = ProductForm()
        form.populate(product)

        login_url = reverse('login') + '?next=' + reverse('product_detail', args=[category_slug, subcategory_slug, id])

        context['current_category'] = current_category
        context['current_subcategory'] = current_subcategory
        context['product'] = product
        context['cart'] = cart
        context['form'] = form
        context['login_url'] = login_url

        return render(request, 'product_detail.html', context)

class ShippingPolicyView(View):

    def get(self, request):
        context = {}
        cart = get_cart(request)
        context['cart'] = cart

        return render(request, 'information/shipping_policy.html', context)

class PaymentPolicyView(View):

    def get(self, request):
        context = {}
        cart = get_cart(request)
        context['cart'] = cart

        return render(request, 'information/payment_policy.html', context)

class ReturnPolicyView(View):

    def get(self, request):
        context = {}
        cart = get_cart(request)
        context['cart'] = cart

        return render(request, 'information/return_policy.html', context)

class ReturnLetterView(View):

    def get(self, request):
        context = {}
        cart = get_cart(request)

        form = ReturnLetterForm()
        formset = ReturnItemFormset()

        context['cart'] = cart
        context['form'] = form
        context['formset'] = formset

        return render(request, 'information/return_letter.html', context)

    def post(self, request):
        context = {}
        cart = get_cart(request)
        form = ReturnLetterForm(request.POST)
        formset = ReturnItemFormset(request.POST)

        context['cart'] = cart
        context['form'] = form
        context['formset'] = formset
        if form.is_valid():
            return_letter, created = ReturnLetter.objects.get_or_create(
                first_name=form.cleaned_data['first_name'],
                middle_name=form.cleaned_data['middle_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                phone_number=form.cleaned_data['phone_number'],
                receive_order_date=form.cleaned_data['receive_order_date'],
                order_number=form.cleaned_data['order_number'],
                bank_card_number=form.cleaned_data['bank_card_number'],
                fml_card_owner=form.cleaned_data['fml_card_owner'],
                comment=form.cleaned_data['comment']
            )
            if formset.is_valid():
                for data in formset.cleaned_data:
                    if data:
                        item = ReturnItem(
                            return_letter=return_letter,
                            product_name=data['product_name'],
                            quantity=data['quantity'],
                            total_price=data['total_price'],
                            return_reason=data['return_reason']
                        )
                        item.save()

                messages.info(request, 'Ваше заявление на возврат товара успешно отправлено')

                send_return_letter_mail_for_admin(return_letter)

                return redirect(reverse('return_letter'))
        return render(request, 'information/return_letter.html', context)

class PrivacyPolicyView(View):

    def get(self, request):
        context = {}
        cart = get_cart(request)
        context['cart'] = cart
        context['shop_domain_name'] = settings.SHOP_DOMAIN_NAME

        return render(request, 'information/privacy_policy.html', context)

class ClothesSizeView(View):

    def get(self, request):
        context = {}
        cart = get_cart(request)
        context['cart'] = cart

        return render(request, 'information/clothes_size.html', context)

class OfferPolicyView(View):

    def get(self, request):
        context = {}
        cart = get_cart(request)
        context['cart'] = cart
        context['shop_domain_name'] = settings.SHOP_DOMAIN_NAME

        return render(request, 'information/offer_policy.html', context)

class AboutUsView(View):

    def get(self, request):
        context = {}
        cart = get_cart(request)
        context['cart'] = cart
        context['shop_domain_name'] = settings.SHOP_DOMAIN_NAME

        return render(request, 'information/about_us.html', context)

