from django.shortcuts import render
from .models import Review
from booking.models import Field
from django.shortcuts import get_object_or_404

def review_list(request, field_id):
    field = get_object_or_404(Field, id=field_id);
    reviews = Review.objects.filter(field=field).order_by('-created_at')
    return render(request, 'all_reviews.html', {'reviews': reviews, 'field': field, 'show_navbar': True})


# Create your views here.
