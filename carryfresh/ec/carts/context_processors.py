from .models import Cart, CartItem
from .views import _cart_id

def counter(request):
    cart_count = 0

    if 'admin' not in request.path:
        try:
            if request.user.is_authenticated:
                # For authenticated users, associate the cart directly with the user
                cart_items = CartItem.objects.filter(user=request.user)
            else:
                # For non-authenticated users, use the cart_id
                cart = Cart.objects.filter(cart_id=_cart_id(request)).first()
                if cart:
                    cart_items = CartItem.objects.filter(cart=cart)
                else:
                    cart_items = []

            for cart_item in cart_items:
                cart_count += cart_item.quantity
        except Cart.DoesNotExist:
            cart_count = 0

    return {'cart_count': cart_count}
