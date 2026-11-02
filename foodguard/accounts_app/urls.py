from django.urls import path
from . import views

urlpatterns = [
    path('register', views.register, name='register'),
    path('login', views.user_login, name='login'),
    path('logout', views.user_logout, name='logout'),
    path('vendors', views.vendors, name='vendors'),
    path('vendor/<int:pk>', views.vendor_detail, name='vendor_detail'),

]