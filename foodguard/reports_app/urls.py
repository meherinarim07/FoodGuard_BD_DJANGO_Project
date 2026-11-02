from django.urls import path
from . import views

urlpatterns = [
    path('reports', views.reports, name='reports'),
    path('my_reports', views.my_reports, name='my_reports'),
    path('report/<int:pk>', views.report_detail, name='report_detail'),
    path('report_create', views.report_create, name='report_create'),
]