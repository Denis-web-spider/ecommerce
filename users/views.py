from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy

from .forms import RegistrationForm, LoginForm, AccountDetailForm

from cart.views import get_cart
from cart.models import Order

CustomUser = get_user_model()

class LoginView(View):

    def get(self, request):
        form = LoginForm()
        cart = get_cart(request)
        context = {
            'form': form,
            'cart': cart,
            'next': request.GET.get('next', '')
        }
        return render(request, 'registration/login.html', context)

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                if request.GET.get('next', None):
                    return HttpResponseRedirect(request.GET['next'])
                return HttpResponseRedirect(reverse('home'))
        cart = get_cart(request)
        context = {
            'form': form,
            'cart': cart
        }
        return render(request, 'registration/login.html', context)

class RegistrationView(View):

    def get(self, request):
        form = RegistrationForm()
        cart = get_cart(request)
        context = {
            'form': form,
            'cart': cart
        }
        return render(request, 'registration/registration.html', context)

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            password = form.cleaned_data['password1']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']

            new_user = CustomUser.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                password=password
            )
            new_user.save()

            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect(reverse('home'))
        cart = get_cart(request)
        context = {
            'form': form,
            'cart': cart
        }
        return render(request, 'registration/registration.html', context)

class ClientAccountView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')

    def get(self, request):
        context = {}
        cart = get_cart(request)

        user = request.user
        orders = Order.objects.filter(cart__owner=user).order_by('-created_at')
        form = AccountDetailForm(
            initial={
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone_number': user.phone_number,
                'email': user.email
            }
        )

        context['cart'] = cart
        context['orders'] = orders
        context['form'] = form

        return render(request, 'client_account.html', context)

    def post(self, request):

        user = request.user

        form = AccountDetailForm(request.POST)
        if form.is_valid():
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.phone_number = form.cleaned_data['phone_number']
            user.email = form.cleaned_data['email']
            user.save()
            messages.info(request, 'Ваши личные данные успешно изменены')
        return HttpResponseRedirect(reverse('client_account'))
