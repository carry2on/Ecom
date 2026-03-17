from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), 
    path('abouts/', views.about, name='about'),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path('register/', views.register_user, name='register'), 
    path('product/<int:pk>', views.product, name='product'),
    path('category/<str:foo>', views.category, name='category'),
    path('category_summary/', views.category_summary, name='category_summary'),
    
    # Profile & User settings
    path('update_user/', views.update_user, name='update_user'),
    path('update_info/', views.update_info, name='update_info'),
    path('update_password/', views.update_password, name='update_password'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('search/', views.search, name='search'),
]