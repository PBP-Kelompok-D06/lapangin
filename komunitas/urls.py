from django.urls import path
from . import views

app_name = 'komunitas'

urlpatterns = [
    path('', views.komunitas_list, name='komunitas_list'),
    path('create/', views.komunitas_create, name='komunitas_create'),
    path('<int:pk>/edit/', views.komunitas_edit, name='komunitas_edit'),
    path('<int:pk>/delete/', views.komunitas_delete, name='komunitas_delete'),
    path('requests/', views.request_komunitas_list, name='request_list'),
    path('requests/<int:pk>/approve/', views.request_komunitas_approve, name='request_approve'),
    path('requests/<int:pk>/reject/', views.request_komunitas_reject, name='request_reject'),
]