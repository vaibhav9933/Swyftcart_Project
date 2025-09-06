from django.shortcuts import render, redirect
from accounts.models import Account, ContactMessage, UserProfile
from django.shortcuts import get_object_or_404
from .forms import RegisterationForm , UserForm, UserProfileForm
from django.contrib import messages , auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .forms import ContactForm



#VERIFICATION EMAIL
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


from carts.views import _cart_id
from carts.models import Cart, CartItem
import requests
from orders.models import Order , OrderProduct

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegisterationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split('@')[0]  # Simple username generation from email

            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password
            )
            user.phone_number = phone_number
            user.is_active = True  # Ensure user can log in
            user.save()

            #USER ACTIVATION 
            current_site = get_current_site(request)
            mail_subject = "Please activate your account!"
            message = render_to_string("accounts/account_verification_email.html", {
                "user": user,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user),
                }) 
            to_email = email
            email_message = EmailMessage(mail_subject, message, to=[to_email])
            email_message.content_subtype = "html"  # Ensures HTML email
            email_message.send()

            #messages.success(request, "Thank you For Registering with us. we have send you a verification email to your address please verify it....")
            return redirect('/accounts/login/?command=verification&email='+email)

    else:
        form = RegisterationForm()

    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)


def login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        if not email or not password:
            messages.error(request, "Please enter both email and password")
            return redirect('login')
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_items = CartItem.objects.filter(cart=cart)
                    session_var_id_list = []
                    session_cart_items = []
                    for item in cart_items:
                        variation = item.variation.all()
                        var_ids = sorted([v.id for v in variation])
                        session_var_id_list.append(var_ids)
                        session_cart_items.append(item)

                    user_cart_items = CartItem.objects.filter(user=user)
                    user_var_id_list = []
                    user_cart_item_ids = []
                    for item in user_cart_items:
                        existing_variation = item.variation.all()
                        existing_ids = sorted([v.id for v in existing_variation])
                        user_var_id_list.append(existing_ids)
                        user_cart_item_ids.append(item.id)

                    for idx, session_var_ids in enumerate(session_var_id_list):
                        if session_var_ids in user_var_id_list:
                            index = user_var_id_list.index(session_var_ids)
                            item_id = user_cart_item_ids[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += session_cart_items[idx].quantity
                            item.save()
                            session_cart_items[idx].delete()
                        else:
                            session_cart_items[idx].user = user
                            session_cart_items[idx].cart = None
                            session_cart_items[idx].save()
            except Exception as e:
                pass
            auth.login(request, user)
            messages.success(request,"You are now logged in.")
            url = request.META.get("HTTP_REFERER")
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split("=") for x in query.split("&"))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')
        else:
            messages.error(request, "Invalid login credentials")
            return redirect('login')
    return render(request, 'accounts/login.html')


@login_required(login_url = "login")
def logout(request):
    auth.logout(request)
    messages.success(request,"You are Succesfully logout")
    return redirect('login')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request,"Congratulations! Your Account is activated.")
        return redirect("login")
    else:
        messages.error(request, "Invalid Activation Link!")
        return redirect("register")
    



@login_required(login_url = "login")
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()

    userprofile, created = UserProfile.objects.get_or_create(user_id=request.user.id)
    context = {
        'orders_count': orders_count,
        'userprofile':userprofile,
    }
    return render(request, 'accounts/dashboard.html', context)


COMMON_EMAIL_TYPOS = ["gamil.com", "gmial.com", "gnail.com", "gmaill.com"]

def forgotpassword(request):
    if request.method == "POST":
        email = request.POST["email"].strip()

        # Step 1: Validate format
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email format.")
            return redirect('forgotpassword')

        # Step 2: Catch common typos
        for typo in COMMON_EMAIL_TYPOS:
            if email.lower().endswith(typo):
                corrected_email = email.lower().replace(typo, "gmail.com")
                messages.error(request, f"Invalid domain — did you mean {corrected_email}?")
                return redirect('forgotpassword')

        # Step 3: Continue with your original logic
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email=email)

            # RESET PASSWORD EMAIL
            current_site = get_current_site(request)
            mail_subject = "Reset Your Password!"
            message = render_to_string("accounts/reset_password_email.html", {
                "user": user,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user),
            })
            to_email = email
            email_message = EmailMessage(mail_subject, message, to=[to_email])
            email_message.content_subtype = "html"  # Ensures HTML email
            email_message.send()

            messages.success(request, "Password reset email has been sent to your Email Address.")
            return redirect('login')
        else:
            messages.error(request, "Account does not exist!")
            return redirect('forgotpassword')

    return render(request, 'accounts/forgotpassword.html')

def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, "Please reset your Password")
        return redirect('resetPassword')
    else:
        messages.error(request, "This link has expired!")
        return redirect('login')

def resetPassword(request):
    if request.method =="POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,"Password reset Successful.")
            return redirect("login")
        else:
            messages.error(request,"Password do not match!")
            return redirect("resetpassword")
    else:
        return render(request,'accounts/resetPassword.html')
    
@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user,is_ordered = True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/my_orders.html', context)

@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('edit_profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile':userprofile,
    }
    return render(request, 'accounts/edit_profile.html', context)

@login_required(login_url='login')
def change_password(request):
    if request.method == "POST":
        current_password = request.POST["current_password"]
        new_password = request.POST["new_password"]
        confirm_password = request.POST["confirm_password"]

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password updated successfully.")
                return redirect('change_password')
            else:
                messages.error(request, "Please enter valid current password")
                return redirect('change_password')
        else:
            messages.error(request, "Password does not match!")
            return redirect('change_password')
    return render(request, 'accounts/change_password.html')

@login_required(login_url='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity

    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal':subtotal,
    }
    return render(request, 'accounts/order_detail.html',context)


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        if name and email and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                message=message
            )
            messages.success(request, "Your message has been sent successfully!")
            return redirect("contact")
        else:
            messages.error(request, "Please fill all fields.")

    return render(request, "contact.html")
