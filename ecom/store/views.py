from django.shortcuts import render
from .models import Product
from django.contrib.auth import authenticate,login,logout
def home(req):
    products=Product.objects.all()
    return render(req,'home.html',{'products':  products})
def about(req):
    return render(req,'about.html')
def login_user(req):
    return render(req,'login.html')
def logout_user(req):
    pass