from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from .models import Product, Cart, CartItem

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart
def add_cart(request, product_id):
    current_user=request.user
    product = Product.objects.get(id=product_id)
    if current_user.is_authenticated:
        # Use filter() instead of get() for handling multiple objects
        cart_items = CartItem.objects.filter(product=product, user=current_user, is_active=True)

        if cart_items.exists():
            # If the item already exists, update the quantity
            cart_item = cart_items.first()
            cart_item.quantity += 1
            cart_item.save()
        else:
            # If the item doesn't exist, create a new one
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user,
                is_active=True,
            )
            cart_item.save()

        return redirect('cart')
        

    else:

        cart_id = _cart_id(request)
        
        
        try:
            cart = Cart.objects.get(cart_id=cart_id)
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=cart_id)
            cart.save()

        try:
            cart_item = CartItem.objects.get(product=product, cart=cart)
            cart_item.quantity += 1
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
            )
            cart_item.save()
        
        return redirect('cart')


def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)

    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except CartItem.DoesNotExist:
        pass

    return redirect('cart')



def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)

        cart_item.delete()
    except CartItem.DoesNotExist:
        pass

    return redirect('cart')


def cart(request,total=0,quantity=0,cart_items=None):
    try:
        tax=0
        delivery_fee = 0
        grand_total=0
        if request.user.is_authenticated:
                cart_items=CartItem.objects.all().filter(user=request.user)
        else:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total+=cart_item.product.price*cart_item.quantity
            quantity+=cart_item.quantity
        tax=(2 * total)/100
        if total < 500:
            delivery_fee = 50
        grand_total=total+tax+delivery_fee

    except ObjectDoesNotExist:
        pass
      
    context={'total':total,
             'quantity':quantity,
             'cart_items':cart_items,
             'tax':tax,
             'delivery_fee':delivery_fee,
             'grand_total':grand_total,

             }
    return render(request, 'app/cart.html',context)

@login_required(login_url="login")
def checkout(request,total=0,quantity=0,cart_items=None):
    try:
        tax=0
        delivery_fee=0
        grand_total=0
        if request.user.is_authenticated:
                cart_items=CartItem.objects.all().filter(user=request.user)
                user=request.user
        else:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total+=cart_item.product.price*cart_item.quantity
            quantity+=cart_item.quantity
        tax=(2 * total)/100
        if total < 500:
            delivery_fee = 50
        grand_total=total+tax+delivery_fee

    except ObjectDoesNotExist:
        pass
      
    context={'total':total,
             'quantity':quantity,
             'cart_items':cart_items,
             'tax':tax,
             'delivery_fee':delivery_fee,
             'grand_total':grand_total,
             'user':user,
             

             }
    return render(request,'app/checkout.html',context)
