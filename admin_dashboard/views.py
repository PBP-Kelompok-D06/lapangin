from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Avg
from .models import Lapangan, VarianLapangan, WarnaLapangan, KategoriLapangan, GaleriLapangan
from komunitas.models import Komunitas, RequestKomunitas
from django.http import JsonResponse
import json

def is_admin(user):
    return user.is_staff or user.groups.filter(name='Admin').exists()

@login_required
@user_passes_test(is_admin)
def dashboard_home(request):
    """Halaman utama dashboard dengan overview produk"""
    context = {
        'total_lapangan': Lapangan.objects.filter(pemilik=request.user).count(),
        'total_komunitas': Komunitas.objects.filter(dibuat_oleh=request.user).count(),
        'pending_requests': RequestKomunitas.objects.filter(status='pending').count(),
    }
    return render(request, 'admin_dashboard/dashboard_home.html', context)


@login_required
@user_passes_test(is_admin)
def lapangan_list(request):
    """Menampilkan daftar semua lapangan milik admin"""
    jenis_filter = request.GET.get('jenis', '')
    lokasi_filter = request.GET.get('lokasi', '')
    
    lapangan_list = Lapangan.objects.filter(pemilik=request.user)
    
    if jenis_filter:
        lapangan_list = lapangan_list.filter(jenis=jenis_filter)
    if lokasi_filter:
        lapangan_list = lapangan_list.filter(lokasi__icontains=lokasi_filter)
    
    context = {
        'lapangan_list': lapangan_list,
        'jenis_choices': Lapangan.JENIS_CHOICES,
    }
    return render(request, 'admin_dashboard/lapangan_list.html', context)


@login_required
@user_passes_test(is_admin)
def lapangan_create(request):
    """Form untuk membuat lapangan baru"""
    if request.method == 'POST':
        try:
            # Ambil data dari form
            lapangan = Lapangan.objects.create(
                nama=request.POST.get('nama'),
                jenis=request.POST.get('jenis'),
                lokasi=request.POST.get('lokasi'),
                harga_per_jam=request.POST.get('harga'),
                deskripsi=request.POST.get('deskripsi', ''),
                fasilitas=request.POST.get('fasilitas', ''),
                pemilik=request.user
            )
            
            if request.FILES.get('foto_utama'):
                lapangan.foto_utama = request.FILES['foto_utama']
                lapangan.save()
            
            # Handle varian
            varian_data = request.POST.getlist('varian[]')
            stock_data = request.POST.getlist('stock[]')
            for varian, stock in zip(varian_data, stock_data):
                if varian:
                    VarianLapangan.objects.create(
                        lapangan=lapangan,
                        ukuran=varian,
                        stock=int(stock) if stock else 1
                    )
            
            # Handle warna
            warna_names = request.POST.getlist('warna_nama[]')
            warna_hex = request.POST.getlist('warna_hex[]')
            for nama, hex_code in zip(warna_names, warna_hex):
                if nama and hex_code:
                    WarnaLapangan.objects.create(
                        lapangan=lapangan,
                        nama_warna=nama,
                        kode_hex=hex_code
                    )
            
            # Handle kategori
            kategori_data = request.POST.getlist('kategori[]')
            for kategori in kategori_data:
                if kategori:
                    KategoriLapangan.objects.create(
                        lapangan=lapangan,
                        nama_kategori=kategori
                    )
            
            messages.success(request, 'Lapangan berhasil ditambahkan!')
            return redirect('admin_dashboard:lapangan_list')
            
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
    
    context = {
        'jenis_choices': Lapangan.JENIS_CHOICES,
        'ukuran_choices': VarianLapangan.UKURAN_CHOICES,
    }
    return render(request, 'admin_dashboard/lapangan_form.html', context)


@login_required
@user_passes_test(is_admin)
def lapangan_edit(request, pk):
    """Edit lapangan yang sudah ada"""
    lapangan = get_object_or_404(Lapangan, pk=pk, pemilik=request.user)
    
    if request.method == 'POST':
        try:
            lapangan.nama = request.POST.get('nama')
            lapangan.jenis = request.POST.get('jenis')
            lapangan.lokasi = request.POST.get('lokasi')
            lapangan.harga_per_jam = request.POST.get('harga')
            lapangan.deskripsi = request.POST.get('deskripsi', '')
            lapangan.fasilitas = request.POST.get('fasilitas', '')
            
            if request.FILES.get('foto_utama'):
                lapangan.foto_utama = request.FILES['foto_utama']
            
            lapangan.save()
            
            messages.success(request, 'Lapangan berhasil diupdate!')
            return redirect('admin_dashboard:lapangan_list')
            
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
    
    context = {
        'lapangan': lapangan,
        'jenis_choices': Lapangan.JENIS_CHOICES,
        'ukuran_choices': VarianLapangan.UKURAN_CHOICES,
    }
    return render(request, 'admin_dashboard/lapangan_form.html', context)


@login_required
@user_passes_test(is_admin)
def lapangan_delete(request, pk):
    """Hapus lapangan"""
    lapangan = get_object_or_404(Lapangan, pk=pk, pemilik=request.user)
    
    if request.method == 'POST':
        lapangan.delete()
        messages.success(request, 'Lapangan berhasil dihapus!')
        return redirect('admin_dashboard:lapangan_list')
    
    return render(request, 'admin_dashboard/lapangan_confirm_delete.html', {'lapangan': lapangan})