from django.urls import path

from .views import SearchAPIView, CartAPIView, ReviewAPIView

urlpatterns = [
    path('search/', SearchAPIView.as_view()),
    path('cart/', CartAPIView.as_view()),
    path('review/', ReviewAPIView.as_view()),
]
