from django.urls import path
from . import views

urlpatterns = [
    # Make sure the name='cart_add' exactly matches what is in your template
    path('add/', views.cart_add, name='cart_add'),
    path('', views.cart_summary, name='cart_summary'),
    path('delete/', views.cart_delete, name='cart_delete'),
    path('update/', views.cart_update, name='cart_update'),
]