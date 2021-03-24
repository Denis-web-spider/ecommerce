from django import forms
from django.forms import ValidationError

from .models import Order

class OrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update(
            {
                'class': 'form-control',
                'form': 'checkout-form',
                'placeholder': 'Иван'
            }
        )
        self.fields['middle_name'].widget.attrs.update(
            {
                'class': 'form-control',
                'form': 'checkout-form',
                'placeholder': 'Иванов'
            }
        )
        self.fields['second_name'].widget.attrs.update(
            {
                'class': 'form-control',
                'form': 'checkout-form',
                'placeholder': 'Иванович'
            }
        )
        self.fields['email'].widget.attrs.update(
            {
                'class': 'form-control',
                'form': 'checkout-form',
                'placeholder': 'ivan@gmail.com'
            }
        )
        self.fields['phone_number'].widget.attrs.update(
            {
                'class': 'form-control',
                'form': 'checkout-form',
                'id': 'phone',
                'data-mask': '+380 00 0000000',
                'placeholder': '+38_ __ _______',
            }
        )
        self.fields['region'].widget.attrs.update(
            {
                'class': 'form-control',
                'form': 'checkout-form',
                'placeholder': 'Харьковская',
            }
        )
        self.fields['locality'].widget.attrs.update(
            {
                'class': 'form-control',
                'form': 'checkout-form',
                'placeholder': 'Богодохов',
            }
        )
        self.fields['post_office'].widget.attrs.update(
            {
                'class': 'form-control',
                'form': 'checkout-form',
                'placeholder': 'Отделение №1: ул. Загорулька, 3',
            }
        )
        self.fields['comment'].widget.attrs.update(
            {
                'class': 'form-control',
                'form': 'checkout-form',
                'placeholder': 'Ваш комментарий',
            }
        )
        self.fields['payment_method'].widget.attrs.update(
            {
                'class': 'custom-control-input',
                'form': 'checkout-form',
            }
        )


    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if len(phone_number) != 15:
            raise ValidationError('Введено некорректное значение')
        return phone_number

    class Meta:
        model = Order
        fields = ['first_name', 'middle_name', 'second_name', 'email', 'phone_number', 'region', 'locality', 'post_office', 'comment', 'payment_method']
        labels = {
            'first_name': 'Имя',
            'middle_name': 'Отчество',
            'second_name': 'Фамилия',
            'email': 'Почта',
            'phone_number': 'Номер телефона',
            'region': 'Область',
            'locality': 'Населенный пункт',
            'post_office': 'Отделение новой почты',
            'comment': 'Комментарий к заказу',
        }
        widgets = {
            'payment_method': forms.RadioSelect
        }

class SearchForm(forms.Form):
    status_choice = forms.ChoiceField(label='Статус', required=False)
    order = forms.ChoiceField(label='Сортировка', required=False)

    status_choice.widget.attrs.update(
        {
            'form': 'search_form',
        }
    )

    order.widget.attrs.update(
        {
            'form': 'search_form',
        }
    )
