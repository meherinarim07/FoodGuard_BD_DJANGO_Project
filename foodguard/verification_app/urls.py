from django.urls import path
from . import views


urlpatterns = [
path('verification_queue', views.verification_queue, name='verification_queue'),
    path('verifications', views.verifications, name='verifications'),
path('report/<int:pk>/verify', views.verification_create, name='verification_create'),

]