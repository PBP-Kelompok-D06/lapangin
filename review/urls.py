from django.urls import path
from .views import review_list, add_review

app_name = 'review'

urlpatterns = [
    path('<int:field_id>/', review_list, name='review_list'),
    path('<int:field_id>/add/', add_review, name='add_review'),
]