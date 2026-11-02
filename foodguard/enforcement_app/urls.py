from django.urls import path
from . import views

urlpatterns = [
    path('alerts', views.alerts, name='alerts'),
    path('alert/<int:pk>/deactivate', views.alert_deactivate, name='alert_deactivate'),
    path('alert/<int:pk>/reactivate', views.alert_reactivate, name='alert_reactivate'),
]