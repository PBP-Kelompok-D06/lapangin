import json
from django.http import JsonResponse
from django.shortcuts import render
from .models import Review
from booking.models import Lapangan as Field
from authbooking.models import Profile
from django.shortcuts import get_object_or_404

def review_list(request, field_id):
    field = get_object_or_404(Field, id=field_id)
    reviews = Review.objects.filter(field=field).order_by('created_at')

    # kalau request dari AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        reviews_data = [
            {
                "user": review.user.user.username,
                "content": review.content,
                "created_at": review.created_at.strftime("%d %b %Y %H:%M")
            }
            for review in reviews
        ]
        return JsonResponse({"reviews": reviews_data})

    # kalau bukan AJAX
    return render(request, 'all_reviews.html', {
        'reviews': reviews,
        'field': field,
        'show_navbar': True
    })


def add_review(request, field_id):
    if request.method == "POST":
        data = json.loads(request.body)
        content = data.get("content")
        field = Field.objects.get(id=field_id)
        rating = data.get("rating")
        user = request.user
        profile = Profile.objects.get(user=user)
        review = Review.objects.create(
            user=profile,
            field=field,
            content=content,
            rating=rating,
        )
        return JsonResponse({
            "success": True,
            "message": "Review berhasil ditambahkan!",
            "review":{
                "user": user.username,
                "content": review.content,
                "rating": review.rating,
                "created_at": review.created_at,
            }
        })
    return JsonResponse({"success": False, "error": "Invalid method"}, status=405)


# Create your views here.
