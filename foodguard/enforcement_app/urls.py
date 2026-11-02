from django.urls import path
from . import views

urlpatterns = [
    path('alerts', views.alerts, name='alerts'),
    path('alert/<int:pk>/deactivate', views.alert_deactivate, name='alert_deactivate'),
    path('alert/<int:pk>/reactivate', views.alert_reactivate, name='alert_reactivate'),
    path('investigations', views.investigations, name='investigations'),
    path('investigation/<int:pk>', views.investigation_detail, name='investigation_detail'),
    path('report/<int:pk>/investigate', views.investigation_create, name='investigation_create'),
    path('investigation/<int:pk>/update', views.investigation_update, name='investigation_update'),
]