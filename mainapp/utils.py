

def get_queryset_that_contains_in_title_every_word_in_search_string(query_set, search_string):
    '''
    Принимает queryset например "Product.objects.all()" и строку например "Джинсы рваные"

    Возвращает queryset, в котором есть каждое слово из search_string

    return:  Product.objects.all().filter(title__icontains='Джинсы').filter(title__icontains='рваные')
    '''
    result_queryset = query_set
    for word in search_string.strip().split():
        result_queryset = result_queryset.filter(title__icontains=word)
    return result_queryset
