from django.conf import settings

from .models import Cart

def get_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(owner=request.user, completed=False)
        cart_uuid = request.session.get(settings.SESSION_CART_UUID_KEY)
        if cart_uuid:
            non_authenticated_cart = Cart.objects.get(uuid=cart_uuid)
            for item in non_authenticated_cart.items.all():
                item.cart = cart
                item.save()
            non_authenticated_cart.delete()
            del request.session[settings.SESSION_CART_UUID_KEY]
    else:
        cart_uuid = request.session.get(settings.SESSION_CART_UUID_KEY)
        if cart_uuid:
            cart = Cart.objects.get(uuid=cart_uuid)
        else:
            cart = Cart.objects.create()
            request.session[settings.SESSION_CART_UUID_KEY] = cart.uuid.hex
    return cart
