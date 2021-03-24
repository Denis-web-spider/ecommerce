from django.urls import path

from .views import RegistrationView, LoginView, ClientAccountView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('my_account/', ClientAccountView.as_view(), name='client_account')
]
