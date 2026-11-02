from django.urls import path
from . import views

urlpatterns = [
    path('reports', views.reports, name='reports'),
    path('my_reports', views.my_reports, name='my_reports'),
    path('report/<int:pk>', views.report_detail, name='report_detail'),
    path('report_create', views.report_create, name='report_create'),
    path('report/<int:pk>/update', views.report_update, name='report_update'),
    path('report/<int:pk>/delete', views.report_delete, name='report_delete'),

    path('report/<int:pk>/evidence', views.evidence_create, name='evidence_create'),
    path('evidence/<int:pk>/update', views.evidence_update, name='evidence_update'),
    path('evidence/<int:pk>/delete', views.evidence_delete, name='evidence_delete'),

    path('awareness', views.awareness, name='awareness'),
    path('post/<int:pk>', views.post_detail, name='post_detail'),
    path('post_create', views.post_create, name='post_create'),
    path('post/<int:pk>/update', views.post_update, name='post_update'),
    path('post/<int:pk>/delete', views.post_delete, name='post_delete'),

]