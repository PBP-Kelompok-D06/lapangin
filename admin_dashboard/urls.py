from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('lapangan/', views.lapangan_list, name='lapangan_list'),
    path('lapangan/create/', views.lapangan_create, name='lapangan_create'),
    path('lapangan/<int:pk>/edit/', views.lapangan_edit, name='lapangan_edit'),
    path('lapangan/<int:pk>/delete/', views.lapangan_delete, name='lapangan_delete'),
]