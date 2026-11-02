from django.urls import path
from . import views

urlpatterns = [
    path('register', views.register, name='register'),
    path('login', views.user_login, name='login'),
    path('logout', views.user_logout, name='logout'),
    path('vendors', views.vendors, name='vendors'),
    path('vendor/<int:pk>', views.vendor_detail, name='vendor_detail'),
    path('vendor_create', views.vendor_create, name='vendor_create'),
    path('vendor/<int:pk>/update', views.vendor_update, name='vendor_update'),
    path('vendor/<int:pk>/delete', views.vendor_delete, name='vendor_delete'),
    path('profile', views.profile, name='profile'),
    path('profile/update', views.profile_update, name='profile_update'),

]