from django.urls import path
from .views import review_list

app_name = 'review'

urlpatterns = [
    path('<int:field_id>/', review_list, name='review_list'),
]