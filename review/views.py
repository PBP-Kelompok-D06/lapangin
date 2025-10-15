import json
from django.http import JsonResponse
from django.shortcuts import render
from .models import Review
from booking.models import Lapangan as Field
from django.shortcuts import get_object_or_404

def review_list(request, field_id):
    field = get_object_or_404(Field, id=field_id)
    reviews = Review.objects.filter(field=field).order_by('created_at')

    # kalau request dari AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        reviews_data = [
            {
                "user": review.user.username,
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
        review = Review.objects.create(
            user=request.user,
            field=field,
            content=content,
            rating=rating,
            created_at=data.get("created_at"),
        )
        return JsonResponse({
            "success": True,
            "message": "Review berhasil ditambahkan!",
            "review":{
                "user": review.user.username,
                "content": review.content,
                "rating": review.rating,
                "created_at": review.created_at,
            }
        })
    return JsonResponse({"success": False, "error": "Invalid method"}, status=405)


# Create your views here.
