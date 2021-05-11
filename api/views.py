from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from mainapp.models import Product, Review
from mainapp.templatetags.category_list_tags import remove_code_from_product_title

from cart.views import get_cart
from cart.models import CartItem

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

class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        cart = get_cart(request)
        cart_info = {
            'cart_items_quantity': cart.total_quantity,
            'cart_total_price' : cart.total_price,
        }

        return Response(cart_info)

    def post(self, request):
        cart = get_cart(request)

        product = Product.objects.get(id=request.POST['product_id'])
        quantity = int(request.POST['quantity'])
        color = request.POST.get('color', '')
        size = request.POST.get('size', '')

        item, created = CartItem.objects.get_or_create(cart=cart, product=product, size=size, color=color)
        if created:
            item.quantity = quantity
            item.save()
        else:
            item.quantity += quantity
            item.save()

        return Response(f'Item with id {item.id} was added successfully!')

    def patch(self, request):
        cart = get_cart(request)
        items = cart.items.all()

        item_id = int(request.POST.get('id'))
        item_quantity = int(request.POST.get('quantity'))

        item = get_object_or_404(items, id=item_id)
        item.quantity = item_quantity
        item.save()

        return Response(f'Item with id {item.id} was updated successfully')

    def delete(self, request):
        cart = get_cart(request)
        items = cart.items.all()

        item_id = int(request.POST.get('id'))

        item = get_object_or_404(items, id=item_id)
        item.delete()

        return Response(f'Item with id {item_id} was deleted successfully')

class ReviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        product = Product.objects.get(id=request.POST['product_id'])
        user = request.user
        ratting = int(request.POST['ratting'])
        review = request.POST['review']
        first_name = request.POST['first_name']
        second_name = request.POST['second_name']

        review_object, created = Review.objects.get_or_create(product=product, user=user)
        review_object.first_name = first_name
        review_object.second_name = second_name
        review_object.ratting = ratting
        review_object.review = review
        review_object.save()

        return Response({'created': created})

    def delete(self, request):

        user = request.user
        product_id = request.POST['product_id']
        review = get_object_or_404(Review, product__id=product_id, user=user)
        review.delete()

        return Response({'deleted': True})
