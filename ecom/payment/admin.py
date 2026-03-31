from django.contrib import admin
from unfold.admin import ModelAdmin, StackedInline
from .models import ShippingAddress, Order, OrderItem

@admin.register(ShippingAddress)
class ShippingAddressAdmin(ModelAdmin):
    pass

@admin.register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    pass

# Create an OrderItem Inline using Unfold's StackedInline
class OrderItemInline(StackedInline):
    model = OrderItem
    extra = 0

# Extend our Order Model using Unfold's ModelAdmin
@admin.register(Order)
class OrderAdmin(ModelAdmin):
    
    # 1. REMOVED 'date_shipped' so the calendar widget appears!
    readonly_fields = ['date_ordered']
    
    # 2. Display list remains the same
    fields = [
        'user', 
        'fullname', 
        'email', 
        'ShippingAddress', 
        'amount_paid', 
        'date_ordered', 
        'shipped', 
        'date_shipped'
    ]
    
    inlines = [OrderItemInline]