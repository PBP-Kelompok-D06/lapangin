from django.shortcuts import render

# Create your views here.
def show_landing_page(request):
    """Menampilkan Landing Page (Homepage) Lapang.in."""
    context = {
        'page_title': 'Pesan Lapangan Olahraga Online',
        # Anda dapat menambahkan variabel lain di sini
        'show_navbar': True,
    }
    return render(request, 'landing_page.html', context)