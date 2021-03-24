from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.forms import ModelForm, Form, ValidationError
from django import forms
from django.contrib.auth.password_validation import validate_password

from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class CustomUserChangeForm(UserChangeForm):
    pass

class CustomUserCreationForm(UserCreationForm):
    pass

class LoginForm(Form):
    password1 = forms.CharField(max_length=50, widget=forms.PasswordInput)
    email = forms.CharField(max_length=150)

    field_order = ['email', 'password1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Пароль'
        self.fields['email'].label = 'Электронная почта'

class RegistrationForm(ModelForm):
    password1 = forms.CharField(max_length=50, widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=50, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтвердите пароль'
        self.fields['email'].label = 'Электронная почта'
        self.fields['phone_number'].widget.attrs.update(
            {
                'id': 'phone',
                'data-mask': '+380 00 0000000',
                'placeholder': '+38_ __ _______',
            }
        )

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с данной электронной почтой уже зарегестрирован на сайте')
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if len(phone_number) != 15:
            raise ValidationError('Введено некорректное значение')
        return phone_number

    def clean(self):
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 != password2:
            raise forms.ValidationError({'password1': 'Пароли не совпадают', 'password2': 'Пароли не совпадают'})
        validate_password(password1)
        return self.cleaned_data

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2']

class AccountDetailForm(Form):
    first_name = forms.CharField(max_length=150, label='Имя')
    last_name = forms.CharField(max_length=150, label='Фамилия')
    phone_number = forms.CharField(max_length=20, label='Номер телефона')
    email = forms.EmailField(label='Электронная почта')

    first_name.widget.attrs.update(
        {
            'class': 'form-control',
            'placeholder': 'Имя',
            'form': 'client_info_form',
        }
    )
    last_name.widget.attrs.update(
        {
            'class': 'form-control',
            'placeholder': 'Фамилия',
            'form': 'client_info_form',
        }
    )
    phone_number.widget.attrs.update(
        {
            'class': 'form-control',
            'id': 'phone',
            'data-mask': '+380 00 0000000',
            'placeholder': '+38_ __ _______',
            'form': 'client_info_form',
        }
    )
    email.widget.attrs.update(
        {
            'class': 'form-control',
            'placeholder': 'Электронная почта',
            'form': 'client_info_form',
        }
    )

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if len(phone_number) != 15:
            raise ValidationError('Введено некорректное значение')
        return phone_number
