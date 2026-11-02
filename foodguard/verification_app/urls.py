from django.urls import path
from . import views


urlpatterns = [
path('verification_queue', views.verification_queue, name='verification_queue'),
    path('verifications', views.verifications, name='verifications'),
path('report/<int:pk>/verify', views.verification_create, name='verification_create'),
    path('verification/<int:pk>/update', views.verification_update, name='verification_update'),
    path('verification/<int:pk>/delete', views.verification_delete, name='verification_delete'),
    path('fraud_flags', views.fraud_flags, name='fraud_flags'),
    path('fraudflag/<int:pk>/resolve', views.fraudflag_resolve, name='fraudflag_resolve'),

]