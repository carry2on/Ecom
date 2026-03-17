from django.contrib import admin
from .models import ShippingAddress, Order, OrderItem

admin.site.register(ShippingAddress)
admin.site.register(OrderItem)

# Create an OrderItem Inline
class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0

# Extend our Order Model
class OrderAdmin(admin.ModelAdmin):
    model = Order
    
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

# Re-Register our Order AND OrderAdmin
admin.site.register(Order, OrderAdmin)