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

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с данной электронной почтой уже зарегестрирован на сайте')
        return email

    def clean(self):
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 != password2:
            raise forms.ValidationError({'password1': 'Пароли не совпадают', 'password2': 'Пароли не совпадают'})
        validate_password(password1)
        return self.cleaned_data

    class Meta:
        model = CustomUser
        fields = ['email', 'password1', 'password2']

class AccountDetailForm(Form):
    email = forms.EmailField(label='Электронная почта')

    email.widget.attrs.update(
        {
            'class': 'form-control',
            'placeholder': 'Электронная почта',
            'form': 'client_info_form',
        }
    )

