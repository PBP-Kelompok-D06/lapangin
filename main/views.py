from django.shortcuts import render
from django.core.paginator import Paginator
from booking.models import Lapangan

def show_landing_page(request):
    """Menampilkan Landing Page Lapang.in dengan daftar lapangan dan pagination."""
    jenis_filter = request.GET.get('jenis', 'all')
    rating_filter = request.GET.get('rating', 'all')

    lapangan_list = Lapangan.objects.all()

    # === Filter jenis olahraga ===
    if jenis_filter != 'all':
        lapangan_list = lapangan_list.filter(jenis_olahraga__iexact=jenis_filter)

    # === Filter rating ===
    if rating_filter != 'all':
        if rating_filter == '0':
            # Lapangan yang belum punya ulasan
            lapangan_list = lapangan_list.filter(jumlah_ulasan=0)
        else:
            lapangan_list = lapangan_list.filter(rating__gte=float(rating_filter))

    # === Pagination (16 per halaman) ===
    paginator = Paginator(lapangan_list, 16)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    jenis_list = Lapangan.objects.values_list('jenis_olahraga', flat=True).distinct()

    context = {
        'page_obj': page_obj,
        'jenis_list': jenis_list,
        'selected_jenis': jenis_filter,
        'selected_rating': rating_filter,
        'show_navbar':True,
    }
    return render(request, 'landing_page.html', context)
