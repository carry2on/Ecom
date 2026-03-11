from django.shortcuts import render,redirect
from .models import Product
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .forms import SignUpForm
def home(req):
    products=Product.objects.all()
    return render(req,'home.html',{'products':  products})
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
    messages.success(req,('you ae sucessfully loged out '))
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

            messages.success(req, "Account created successfully!")
            return redirect("home")

    else:
        form = SignUpForm()

    return render(req, "register.html", {"form": form})