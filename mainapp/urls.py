from django.urls import path

from .views import (
    HomePageView,
    CategoryProductsListView,
    SubcategoryProductsListView,
    ProductDetailView,
    SearchView,

    ShippingPolicyView,
    PaymentPolicyView,
    ReturnPolicyView,
    ReturnLetterView,
    PrivacyPolicyView,
    ClothesSizeView,
    OfferPolicyView,
    AboutUsView,

    TestView
)

urlpatterns = [
    path('shipping_policy/', ShippingPolicyView.as_view(), name='shipping_policy'),
    path('payment_policy/', PaymentPolicyView.as_view(), name='payment_policy'),
    path('return_policy/', ReturnPolicyView.as_view(), name='return_policy'),
    path('return_letter/', ReturnLetterView.as_view(), name='return_letter'),
    path('privacy_policy/', PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('clothes_size/', ClothesSizeView.as_view(), name='clothes_size'),
    path('offer_policy/', OfferPolicyView.as_view(), name='offer_policy'),
    path('about_us/', AboutUsView.as_view(), name='about_us'),

    path('test/', TestView.as_view()),

    path('search/', SearchView.as_view(), name='search'),
    path('<str:slug>/', CategoryProductsListView.as_view(), name='category_products'),
    path('<str:category_slug>/<str:subcategory_slug>/', SubcategoryProductsListView.as_view(), name='subcategory_products'),
    path('<str:category_slug>/<str:subcategory_slug>/<str:id>/', ProductDetailView.as_view(), name='product_detail'),
    path('', HomePageView.as_view(), name='home'),
]
