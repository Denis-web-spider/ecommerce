from django import forms
from django.forms import ValidationError, formset_factory

from .models import ReturnLetter, ReturnItem
from .utils import product_sizes_comparison_for_sort

class ProductForm(forms.Form):
    quantity = forms.CharField(initial='1', label='Количество', label_suffix=':')
    size = forms.ChoiceField(label='Размер', label_suffix=':')
    color = forms.ChoiceField(label='Цвет', label_suffix=':')
    product_id = forms.IntegerField(widget=forms.HiddenInput())

    SIZE_CHOICES = [
        ('', '--- Выберите значение ---')
    ]

    COLOR_CHOICES = [
        ('', '--- Выберите значение ---')
    ]

    quantity.widget.attrs.update({'form': 'add_to_cart_form'})
    size.widget.attrs.update({'form': 'add_to_cart_form'})
    color.widget.attrs.update({'form': 'add_to_cart_form'})
    product_id.widget.attrs.update({'form': 'add_to_cart_form'})

    def populate(self, product):
        sizes = product.size_specifications()
        colors = product.color_specifications()

        if sizes:
            for size in sizes:
                self.SIZE_CHOICES.append((size, size))
            self.fields['size'].choices = self.SIZE_CHOICES
        else:
            self.fields['size'].required = False

        if colors:
            for color in colors:
                self.COLOR_CHOICES.append((color, color))
            self.fields['color'].choices = self.COLOR_CHOICES
        else:
            self.fields['color'].required = False

        self.fields['product_id'].widget.attrs.update({
            'value': f'{product.id}'
        })

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        try:
            int(quantity)
        except ValueError:
            raise ValidationError('Введите число в это поле')
        else:
            return quantity

class SearchForm(forms.Form):
    title = forms.CharField(label='Поиск', label_suffix=':', required=False)
    sort = forms.ChoiceField(label='Сортировка', label_suffix=':', required=False)
    from_price = forms.CharField(label='от', label_suffix=':', required=False, help_text='Минимлаьная цена')
    to_price = forms.CharField(label='до', label_suffix=':', required=False, help_text='Максимальная цена')
    size = forms.ChoiceField(label='Размер', label_suffix=':', required=False)
    color = forms.ChoiceField(label='Цвет', label_suffix=':', required=False)

    SORT_CHOICES = [
        ('-ratting', 'По умолчанию'),
        ('title', 'Наименование (А -> Я)'),
        ('-title', 'Наименование (Я -> А)'),
        ('-ratting', 'Рейтинг (по убыванию)'),
        ('ratting', 'Рейтинг (по возростанию)'),
        ('-price', 'Цена (по убыванию)'),
        ('price', 'Цена (по возрастанию)')
    ]

    SIZE_CHOICES = [
        ('', 'Любой размер')
    ]

    COLOR_CHOICES = [
        ('', 'Любой цвет')
    ]

    title.widget.attrs.update({
        'placeholder': 'Поиск',
        'form': 'search_form'
    })
    sort.widget.attrs.update({
        'form': 'search_form'
    })
    from_price.widget.attrs.update({
        'placeholder': 'От 0',
        'form': 'search_form',
        'class': 'only-digits',
    })
    to_price.widget.attrs.update({
        'placeholder': 'До 99999',
        'form': 'search_form',
        'class': 'only-digits',
    })
    size.widget.attrs.update({
        'form': 'search_form',
    })
    color.widget.attrs.update({
        'form': 'search_form',
    })

    def populate_choice_fields(self, products):

        #for product in products:
        #    for size in product.size_specifications():
        #        if (size, size) not in self.COLOR_CHOICES:
        #            self.SIZE_CHOICES.append((size, size))

        #for product in products:
        #    for color in product.color_specifications():
        #        if (color, color) not in self.COLOR_CHOICES:
        #            self.COLOR_CHOICES.append((color, color))

        self.fields['sort'].choices = self.SORT_CHOICES
        self.fields['size'].choices = self.SIZE_CHOICES
        self.fields['color'].choices = self.COLOR_CHOICES

    def clean_from_price(self):
        from_price = self.cleaned_data['from_price'].strip()
        if from_price:
            try:
                from_price = int(from_price)
            except ValueError:
                raise ValidationError('Введено некорректное значение')
            else:
                return from_price
        else:
            from_price = 0
            return from_price

    def clean_to_price(self):
        to_price = self.cleaned_data['to_price'].strip()
        if to_price:
            try:
                to_price = int(to_price)
            except ValueError:
                raise ValidationError('Введено некорректное значение')
            else:
                return to_price
        else:
            to_price = 999999999
            return to_price

class ReturnLetterForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['first_name'].widget.attrs.update(
            {
                'class': 'form-control',
                'form': 'return_letter_form',
                'placeholder': 'Иван',
            }
        )
        self.fields['middle_name'].widget.attrs.update(
            {
                'class': 'form-control',
                'form': 'return_letter_form',
                'placeholder': 'Иванович',
            }
        )
        self.fields['last_name'].widget.attrs.update(
            {
                'class': 'form-control',
                'form': 'return_letter_form',
                'placeholder': 'Иванов',
            }
        )
        self.fields['email'].widget.attrs.update(
            {
                'class': 'form-control',
                'form': 'return_letter_form',
                'placeholder': 'ivan@gmail.com',
            }
        )
        self.fields['fml_card_owner'].widget.attrs.update(
            {
                'class': 'form-control',
                'form': 'return_letter_form',
                'placeholder': 'Иванов Иван Иванович',
            }
        )
        self.fields['receive_order_date'].widget.attrs.update(
            {
                'class': 'form-control',
                'form': 'return_letter_form',
                'placeholder': '2021-01-01',
                'data-mask': '0000-00-00',
            }
        )
        self.fields['order_number'].widget.attrs.update(
            {
                'class': 'form-control',
                'form': 'return_letter_form',
                'placeholder': '1',
            }
        )
        self.fields['phone_number'].widget.attrs.update(
            {
                'class': 'form-control',
                'form': 'return_letter_form',
                'id': 'phone',
                'data-mask': '+380 00 0000000',
                'placeholder': '+38_ __ _______',
            }
        )
        self.fields['bank_card_number'].widget.attrs.update(
            {
                'class': 'form-control',
                'form': 'return_letter_form',
                'data-mask': '0000 0000 0000 0000',
                'placeholder': '0000 0000 0000 0000',
            }
        )
        self.fields['comment'].widget.attrs.update(
            {
                'class': 'form-control',
                'form': 'return_letter_form',
                'placeholder': 'Ваш комментарий'
            }
        )
        self.fields['comment'].requered = False

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if len(phone_number) != 15:
            raise ValidationError('Введено некорректное значение')
        return phone_number

    def clean_bank_card_number(self):
        bank_card_number = self.cleaned_data['bank_card_number']
        if len(bank_card_number) != 19:
            raise ValidationError('Введено некорректное значение')
        return bank_card_number

    class Meta:
        model = ReturnLetter
        fields = [
            'first_name',
            'middle_name',
            'last_name',
            'email',
            'phone_number',
            'receive_order_date',
            'order_number',
            'bank_card_number',
            'fml_card_owner',
            'comment'
        ]

class ReturnItemForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product_name'].widget.attrs.update(
            {
                'class': 'form-control',
                'form': 'return_letter_form',
                'placeholder': 'Куртка мужская с капюшоном 187P449',
            }
        )
        self.fields['quantity'].widget.attrs.update(
            {
                'class': 'form-control',
                'form': 'return_letter_form',
                'placeholder': '10',
            }
        )
        self.fields['total_price'].widget.attrs.update(
            {
                'class': 'form-control',
                'form': 'return_letter_form',
                'step': '1',
                'placeholder': '7590',
            }
        )
        self.fields['return_reason'].widget.attrs.update(
            {
                'class': 'form-control',
                'form': 'return_letter_form',
            }
        )
        self.fields['product_name'].required = True
        self.fields['quantity'].required = True
        self.fields['total_price'].required = True
        self.fields['return_reason'].required = True

    class Meta:
        model = ReturnItem
        fields = [
            'product_name',
            'quantity',
            'total_price',
            'return_reason'
        ]

ReturnItemFormset = formset_factory(ReturnItemForm, extra=3)
