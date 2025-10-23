# gallery/urls.py
from django.urls import path
from . import views

app_name = 'gallery'

urlpatterns = [
    path('', views.GalleryListView.as_view(), name='list'),
    path('id/<int:pk>/', views.GalleryDetailByPKView.as_view(), name='detail_by_pk'),
    path('<slug:slug>/', views.GalleryDetailView.as_view(), name='detail'),
]
