from rest_framework.views import APIView
from rest_framework.response import Response

from mainapp.models import Product
from mainapp.templatetags.category_list_tags import remove_code_from_product_title

class SearchAPIView(APIView):
    def get(self, request, format=None):
        search_query = request.GET['search_query']
        category_title = request.GET.get('category', '')
        subcategory_title = request.GET.get('subcategory', '')
        subsearch_query = request.GET.get('subsearch_query', '')
        if subsearch_query:
            products = Product.objects.filter(title__icontains=subsearch_query).filter(title__icontains=search_query).exclude(in_stock=False)[:20]
        elif subcategory_title:
            products = Product.objects.filter(title__icontains=search_query, category__category__title=category_title, category__title=subcategory_title).exclude(in_stock=False)[:20]
        elif category_title:
            products = Product.objects.filter(title__icontains=search_query, category__category__title=category_title).exclude(in_stock=False)[:20]
        else:
            products = Product.objects.filter(title__icontains=search_query).exclude(in_stock=False)[:20]
        products_title = []
        for product in products:
            title = remove_code_from_product_title(product.title).strip()
            if not title in products_title:
                products_title.append(f'{remove_code_from_product_title(product.title).strip()}')
        products_title = products_title[:7]

        return Response(products_title)


