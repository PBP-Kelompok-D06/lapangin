from django.views.generic import ListView, DetailView
from .models import Lapangan

class GalleryListView(ListView):
    model = Lapangan
    template_name = 'gallery/gallery_list.html'
    context_object_name = 'lapangans'
    paginate_by = 12

class GalleryDetailView(DetailView):
    model = Lapangan
    template_name = 'gallery/gallery_detail.html'
    context_object_name = 'lapangan'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
