from django.urls import path

from .views import SearchAPIView, CartAPIView

urlpatterns = [
    path('search/', SearchAPIView.as_view()),
    path('cart/', CartAPIView.as_view()),
]
