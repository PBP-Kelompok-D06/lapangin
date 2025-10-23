# gallery/views.py
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Avg, Count
from booking.models import Lapangan   # import model (tidak mengubahnya)

class GalleryListView(ListView):
    model = Lapangan
    template_name = 'gallery/gallery_list.html'
    context_object_name = 'lapangans'
    paginate_by = 12
    ordering = ['-dibuat']  # kalau field 'dibuat' ga ada di model booking, ganti jadi '-id' atau hapus

class GalleryDetailView(DetailView):
    # slug-based (opsional) — biarkan kalau temen nanti pakai slug
    model = Lapangan
    template_name = 'gallery/gallery_detail.html'
    context_object_name = 'lapangan'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        lap = ctx['lapangan']
        reviews = lap.review_set.select_related('user').order_by('-dibuat')
        ctx['reviews'] = reviews
        avg = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        ctx['avg_rating'] = round(avg, 1)
        return ctx

class GalleryDetailByPKView(DetailView):
    # PK-based view — ini yang akan kita gunakan dari landing page
    model = Lapangan
    template_name = 'gallery/gallery_detail.html'
    context_object_name = 'lapangan'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        lap = ctx['lapangan']
        reviews = lap.review_set.select_related('user').order_by('-dibuat')
        ctx['reviews'] = reviews
        avg = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        ctx['avg_rating'] = round(avg, 1)
        return ctx
