from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from .models import Product, Category, Profile
from .forms import SignUpForm, UpdateUserform, ChangePasswordForm, UserInfoForm
import json
from payment.forms import ShippingForm
from payment.models import ShippingAddress
def user_profile(request):
    if request.user.is_authenticated:
        current_profile, created = Profile.objects.get_or_create(user=request.user)
        return render(request, "user_profile.html", {"user_profile": current_profile})
    else:
        messages.error(request, "You Must Be Logged In To View That Page...")
        return redirect('login')

def update_info(request):
    if request.user.is_authenticated:
        # 1. Get BOTH the user's Profile and their Shipping Address from the database
        current_profile, created = Profile.objects.get_or_create(user=request.user)
        shipping_user, created = ShippingAddress.objects.get_or_create(user=request.user)
        
        if request.method == 'POST':
            # 2. Grab the POST data for both forms
            form = UserInfoForm(request.POST, instance=current_profile)
            shipping_form = ShippingForm(request.POST, instance=shipping_user)
            
            # 3. Check if BOTH forms are completely valid
            if form.is_valid() or shipping_form.is_valid():
                form.save()
                shipping_form.save()
                messages.success(request, "Your Info Has Been Updated!!")
                return redirect('home')
        else:
            # 4. Display the pre-filled forms if they just visit the page
            form = UserInfoForm(instance=current_profile)
            shipping_form = ShippingForm(instance=shipping_user)
            
        # 5. Send both forms to the HTML template
        return render(request, "update_info.html", {'form': form, 'shipping_form': shipping_form})
        
    else:
        messages.error(request, "You Must Be Logged In To View That Page...")
        return redirect('login')
def update_user(request):
    if request.user.is_authenticated:
        current_user = request.user
        
        if request.method == 'POST':
            user_form = UpdateUserform(request.POST, instance=current_user)
            if user_form.is_valid():
                user = user_form.save()
                login(request, current_user)
                messages.success(request, "Your Profile Has Been Updated!!")
                return redirect('home')
        else:
            user_form = UpdateUserform(instance=current_user)
            
        return render(request, "update_user.html", {'user_form': user_form})
    else:
        messages.error(request, "You Must Be Logged In To View That Page...")
        return redirect('login')

def update_password(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Your password was successfully updated!")
                return redirect('update_user')
            else:
                messages.error(request, "Please correct the errors below.")
        else:
            form = PasswordChangeForm(request.user)
            
        return render(request, 'update_password.html', {'form': form})
    else:
        messages.error(request, "You must be logged in to view that page.")
        return redirect('login')

def home(req):
    products=Product.objects.all()
    return render(req,'home.html',{'products': products})

def about(req):
    return render(req,'about.html')

def login_user(req):
    if req.method == 'POST':
        username = req.POST['username']
        password = req.POST['password']
        user = authenticate(req, username=username, password=password)
        if user is not None:
            login(req, user)
            messages.success(req, "You are successfully logged in")
            return redirect('home')
        else:
            messages.error(req, "Invalid username or password")
            return redirect('login')
    return render(req, 'login.html')

def logout_user(req):
    logout(req)
    messages.success(req,('you are successfully logged out '))
    return redirect('home')

def product(req,pk):
    product=Product.objects.get(id=pk)
    return render(req,'product.html',{'product':product})
def register_user(req):
    if req.method == "POST":
        form = SignUpForm(req.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(req, username=username, password=password)
            login(req, user)
            messages.success(req, "Account created successfully! Please fill out your shipping info.")
            
            # --- CHANGED THIS LINE ---
            # Now redirects to update_info instead of home
            return redirect("update_info") 
    else:
        form = SignUpForm()
    return render(req, "register.html", {"form": form})

def category(request, foo):
    foo = foo.replace('-', ' ')
    try:
        category = Category.objects.get(name=foo)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products': products, 'category': category})
    except Category.DoesNotExist:
        messages.error(request, "That category doesn't exist...")
        return redirect('home')
    
def category_summary(request):
    categories = Category.objects.all()
    return render(request, 'category_summary.html', {'categories': categories})
def search(request):
    # Check if the user submitted the search form
    if request.method == "POST":
        # Grab the text they typed into the box (name="searched")
        searched = request.POST.get('searched')
        
        # Look up products where the name contains the searched text
        # 'icontains' makes it case-insensitive (ignores uppercase/lowercase)
        searched_products = Product.objects.filter(name__icontains=searched)
        
        return render(request, "search.html", {
            'searched': searched, 
            'searched_products': searched_products
        })
        
    else:
        # If they just went to the /search/ URL directly without searching anything
        return render(request, "search.html", {})
def login_user(req):
    if req.method == 'POST':
        username = req.POST['username']
        password = req.POST['password']

        user = authenticate(req, username=username, password=password)

        if user is not None:
            # 1. GRAB THE GUEST CART BEFORE LOGGING IN!
            # We must rescue the cart before Django destroys the session
            cart_session = req.session.get('session_key')

            # 2. Log the user in
            login(req, user)
            messages.success(req, "You are successfully logged in")
            
            # 3. Handle the Database Cart Merge
            try:
                current_profile = Profile.objects.get(user__id=user.id)
                
                if current_profile.old_cart:
                    old_cart = json.loads(current_profile.old_cart)
                    
                    # Merge guest cart into database cart
                    if cart_session:
                        old_cart.update(cart_session)
                        
                    # Save back to browser and DB
                    req.session['session_key'] = old_cart
                    current_profile.old_cart = str(old_cart).replace("\'", "\"")
                    current_profile.save()
                else:
                    # IF NO OLD CART EXISTS IN DB, SAVE THE GUEST CART
                    if cart_session:
                        req.session['session_key'] = cart_session
                        current_profile.old_cart = str(cart_session).replace("\'", "\"")
                        current_profile.save()
            except Exception as e:
                # This will print the exact issue to your terminal if it fails!
                print("CART ERROR:", e)
                pass
            
            return redirect('home')
        else:
            messages.error(req, "Invalid username or password")
            return redirect('login')

    return render(req, 'login.html')