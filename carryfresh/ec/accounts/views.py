from django.shortcuts import redirect, render
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from .forms import RegistrationForm
from .models import Account
from orders.models import Order,OrderProduct
from carts.models import Cart,CartItem
from carts.views import _cart_id
import requests

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(request, email=email, password=password)

        if user is not None:
            try:
                cart=Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists=CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item=CartItem.objects.filter(cart=cart)

                    for item in cart_item:
                        item.user=user
                        item.save()
            except:
                pass
            auth.login(request, user)
            url=request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                
                if 'next' in params:
                    nextpage = params['next']
                    print("Next Page:", nextpage)
                    return redirect(nextpage)
            except :
                return redirect('dashboard')
        
        else:
            messages.error(request, "Invalid login credentials", extra_tags='error')
            return redirect('login')
    return render(request, 'app/login.html')

def signup(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]

            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password
            )
            user.phone_number = phone_number
            user.save()

            # USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('app/account_verification_email.html',
             {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email  # Fix: Added equal sign
            
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            #messages.success(request, "Account created. Please check your email to activate your account.", extra_tags='success')
            return redirect('/accounts/login/?command=verification&email='+email)

            
    else:
        form = RegistrationForm()

    context = {'form': form}
    return render(request, 'app/signup.html', context)

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, "Logout successful")
    return redirect('login')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64)
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, Account.DoesNotExist):
            user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Account has been activated! You can now login.")
        return redirect('login')
    else:
        messages.error(request, "The activation link is invalid. Maybe your account is already exist",extra_tags='error')
        return redirect('app:index')

def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id,is_ordered=True)
    orders_count=orders.count()
    context={
        'orders':orders,
        'orders_count':orders_count,
        }

    return render(request, 'app/dashboard.html',context)     

def forgotPassword(request):
    if request.method == 'POST':
        email=request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            # Reset password email
            current_site=get_current_site(request)
            mail_subject="Reset Your Password"
            message=render_to_string('app/reset_password_email.html', 
             { 
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)), 
                'token': default_token_generator.make_token(user),
            })
            to_email=email
            send_email =EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, 'Password reset email has been sent to your email address.') 
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist!',extra_tags='error')
            return redirect('forgotPassword') 
    return render(request, 'app/forgotPassword.html')

def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, Account.DoesNotExist):
            user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid']=uid
        messages.success(request,'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.warning(request,"This password reset link is expired or may have been used before.")
        return redirect('login')

def resetPassword(request):
    if request.method=='POST':
        
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']
        if password==confirm_password:
            uid=request.session.get('uid')
            user=Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'Your password has been changed successfully. Please login with new password.',extra_tags='error')
            
            return redirect('login')
        else:
            messages.error(request,'Passwords do not match. Please enter the same password in both fields.',extra_tags='error')
            return redirect('resetPassword')
    else:

        return render(request,'app/resetPassword.html')         
@login_required(login_url='login')
def my_orders(request):
    orders=Order.objects.filter(user=request.user,is_ordered=True).order_by('-created_at')
    context={
        "orders":orders
        }
    
    return render(request,'app/my_orders.html',context)


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password=request.POST['current_password']
        new_password=request.POST['new_password']
        confirm_password=request.POST['confirm_password']
        user=Account.objects.get(username__exact=request.user.username)
        if new_password==confirm_password:
            success= user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request,f"Your Password has been changed successfully")
                return redirect("change_password")
            else:
                messages.error(request,f"Current Password is incorrect!",extra_tags='error')
                return redirect("change_password")
        else:
            messages.error(request,f"New Passwords do not match.Please try again.",extra_tags='error')
            return redirect("change_password")

    return render(request,'app/change_password.html')
    

@login_required(login_url='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal=0
    for i in order_detail:
        subtotal +=i.product_price * i.quantity
    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }
    return render(request, 'app/order_detail.html', context)
@login_required(login_url='login')
def trackorder(request,order_id):
    order = Order.objects.get(order_number=order_id)
    context = {
        
        'order': order,
        
    }
    return render(request,'app/trackorder.html', context)

                                               
    
    
    
