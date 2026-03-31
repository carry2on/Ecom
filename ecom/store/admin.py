from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Category, Product, Customer, Order, Profile

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    pass

@admin.register(Product)
class ProductAdmin(ModelAdmin):
    pass

@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    pass

@admin.register(Order)
class OrderAdmin(ModelAdmin):
    pass

@admin.register(Profile)
class ProfileAdmin(ModelAdmin):
    pass