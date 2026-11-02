from django.urls import path
from . import views


urlpatterns = [
path('verification_queue', views.verification_queue, name='verification_queue'),
path('report/<int:pk>/verify', views.verification_create, name='verification_create'),

]