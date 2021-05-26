from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.core.paginator import Paginator, EmptyPage

def get_queryset_that_contains_in_title_every_word_in_search_string(query_set: QuerySet, search_string: str) -> QuerySet:
    '''
    Принимает queryset например "Product.objects.all()" и строку например "Джинсы рваные"

    Возвращает queryset, в котором есть каждое слово из search_string

    return:  Product.objects.all().filter(title__icontains='Джинсы').filter(title__icontains='рваные')
    '''
    result_queryset = query_set
    for word in search_string.strip().split():
        result_queryset = result_queryset.filter(title__icontains=word)
    return result_queryset

def product_sizes_comparison_for_sort(size):
    sizes = {
        'XXS': 0,
        'XS': 1,
        'S': 2,
        'M': 3,
        'L': 4,
        'XL': 5,
        'XXL': 6,
        'XXXL': 7,
        '4XL': 8,
        '5XL': 9,
        '6XL': 10,
        '7XL': 11,
        '8XL': 12,
    }

    if size.isdigit():
        return int(size)
    if size in sizes:
        return sizes[size]
    else:
        if size.split('-')[0] in sizes:
            return sizes[size.split('-')[0]]
        if size.split('-')[0].isdigit():
            return int(size.split('-')[0])
        else:
            return 13

def products_queryset_searched_sorted_and_filtered(products: QuerySet, request: HttpRequest, all_sizes=False, all_colors=False) -> QuerySet:
    '''Возвращает результат поиска с фильтрами'''

    search_query = request.GET.get('search_query')
    if search_query:
        products = get_queryset_that_contains_in_title_every_word_in_search_string(products, search_query)

    title = request.GET.get('title')
    if title:
        products = get_queryset_that_contains_in_title_every_word_in_search_string(products, title)

    from_price = request.GET.get('from_price', '')
    to_price = request.GET.get('to_price', '')
    if from_price.isdigit():
        from_price = int(from_price)
    else:
        from_price = 0
    if to_price.isdigit():
        to_price = int(to_price)
    else:
        to_price = 99999999999999999999999999999999999999999
    products = products.filter(price__gte=from_price, price__lte=to_price)

    sort = request.GET.get('sort')
    if sort:
        products = products.order_by(sort)

    size = request.GET.get('size')
    if size and not all_sizes:
        for product in products:
            product_sizes = product.size_specifications()
            if size not in product_sizes:
                products = products.exclude(id=product.id)

    color = request.GET.get('color')
    if color and not all_colors:
        for product in products:
            product_colors = product.color_specifications()
            if color not in product_colors:
                products = products.exclude(id=product.id)

    return products

def products_pagination(products, request: HttpRequest):
    '''
    products = Queryset or list

    Принимает products: QuerySet, request: HttpRequest

    page_range это list с номерами страниц, которые появятся в пагинации

    return: page_obj, page_range
    '''

    paginator = Paginator(products, 15)
    page_number = int(request.GET.get('page', 1))

    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        page_obj = paginator.page(1)

    if len(list(paginator.page_range)) <= 10:
        page_range = paginator.page_range
    elif page_number - 6 >= 0:
        page_range = list(paginator.page_range)[page_number - 6:page_number + 5]
        if len(page_range) < 11:
            index = 11 - len(page_range)
            page_range = list(paginator.page_range)[page_number - 6 - index:page_number + 5]
    else:
        page_range = list(paginator.page_range)[:page_number + 9]

    return page_obj, page_range
