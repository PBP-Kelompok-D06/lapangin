from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse

# Import dari BOOKING models (bukan admin_dashboard models)
from booking.models import Booking, SlotTersedia, Lapangan
from komunitas.models import Komunitas, RequestKomunitas
from datetime import date, time, timedelta

# Decorator untuk cek role PEMILIK
def is_pemilik(user):
    """Cek apakah user adalah PEMILIK lapangan"""
    return hasattr(user, 'profile') and user.profile.role == 'PEMILIK'

# Decorator gabungan
def pemilik_required(view_func):
    """Decorator untuk memastikan user adalah PEMILIK"""
    from django.contrib.auth.decorators import user_passes_test
    decorated_view = login_required(user_passes_test(is_pemilik, login_url='/accounts/login/')(view_func))
    return decorated_view


# ==================== DASHBOARD HOME ====================
@pemilik_required
def dashboard_home(request):
    """Halaman utama dashboard dengan overview"""
    # Hitung total lapangan milik pemilik ini
    total_lapangan = Lapangan.objects.filter(pengelola=request.user.profile).count()
    
    # Hitung total komunitas yang dibuat
    total_komunitas = Komunitas.objects.filter(dibuat_oleh=request.user).count()
    
    # Hitung booking pending untuk lapangan milik pemilik ini
    pending_bookings = Booking.objects.filter(
        slot__lapangan__pengelola=request.user.profile,
        status_pembayaran='PENDING'
    ).count()
    
    context = {
        'total_lapangan': total_lapangan,
        'total_komunitas': total_komunitas,
        'pending_requests': RequestKomunitas.objects.filter(status='pending').count(),
        'pending_bookings': pending_bookings,  # Tambahan untuk notifikasi
    }
    return render(request, 'admin_dashboard/dashboard_home.html', context)


# ==================== LAPANGAN MANAGEMENT ====================
@pemilik_required
def lapangan_list(request):
    """Menampilkan daftar semua lapangan milik pemilik"""
    jenis_filter = request.GET.get('jenis', '')
    lokasi_filter = request.GET.get('lokasi', '')
    
    # Filter hanya lapangan milik pemilik yang login
    lapangan_list = Lapangan.objects.filter(pengelola=request.user.profile)
    
    if jenis_filter:
        lapangan_list = lapangan_list.filter(jenis_olahraga=jenis_filter)
    if lokasi_filter:
        lapangan_list = lapangan_list.filter(lokasi__icontains=lokasi_filter)
    
    # Choices untuk jenis olahraga
    jenis_choices = [
        ('Futsal', 'Futsal'),
        ('Bulutangkis', 'Bulutangkis'),
        ('Basket', 'Basket'),
    ]
    
    context = {
        'lapangan_list': lapangan_list,
        'jenis_choices': jenis_choices,
    }
    return render(request, 'admin_dashboard/lapangan_list.html', context)


@pemilik_required
def lapangan_create(request):
    """Form untuk membuat lapangan baru"""
    if request.method == 'POST':
        try:
            # Buat lapangan baru dengan pengelola = profile pemilik yang login
            lapangan = Lapangan.objects.create(
                nama_lapangan=request.POST.get('nama'),
                jenis_olahraga=request.POST.get('jenis'),
                lokasi=request.POST.get('lokasi'),
                harga_per_jam=request.POST.get('harga'),
                deskripsi=request.POST.get('deskripsi', ''),
                fasilitas=request.POST.get('fasilitas', ''),
                pengelola=request.user.profile  # Set pengelola
            )
            
            if request.FILES.get('foto_utama'):
                lapangan.foto_utama = request.FILES['foto_utama']
                lapangan.save()
            
            messages.success(request, 'Lapangan berhasil ditambahkan!')
            return redirect('admin_dashboard:lapangan_list')
            
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
    
    jenis_choices = [
        ('Futsal', 'Futsal'),
        ('Bulutangkis', 'Bulutangkis'),
        ('Basket', 'Basket'),
    ]
    
    context = {
        'jenis_choices': jenis_choices,
    }
    return render(request, 'admin_dashboard/lapangan_form.html', context)


@pemilik_required
def lapangan_edit(request, pk):
    """Edit lapangan yang sudah ada"""
    lapangan = get_object_or_404(Lapangan, pk=pk, pengelola=request.user.profile)
    
    if request.method == 'POST':
        try:
            lapangan.nama_lapangan = request.POST.get('nama')
            lapangan.jenis_olahraga = request.POST.get('jenis')
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
    
    jenis_choices = [
        ('Futsal', 'Futsal'),
        ('Bulutangkis', 'Bulutangkis'),
        ('Basket', 'Basket'),
    ]
    
    context = {
        'lapangan': lapangan,
        'jenis_choices': jenis_choices,
    }
    return render(request, 'admin_dashboard/lapangan_form.html', context)


@pemilik_required
def lapangan_delete(request, pk):
    """Hapus lapangan"""
    lapangan = get_object_or_404(Lapangan, pk=pk, pengelola=request.user.profile)
    
    if request.method == 'POST':
        lapangan.delete()
        messages.success(request, 'Lapangan berhasil dihapus!')
        return redirect('admin_dashboard:lapangan_list')
    
    return render(request, 'admin_dashboard/lapangan_confirm_delete.html', {'lapangan': lapangan})


# ==================== BOOKING MANAGEMENT (NEW!) ====================
@pemilik_required
def booking_pending_list(request):
    """Menampilkan daftar booking PENDING untuk di-approve/reject"""
    # Filter booking PENDING untuk lapangan milik pemilik yang login
    pending_bookings = Booking.objects.filter(
        slot__lapangan__pengelola=request.user.profile,
        status_pembayaran='PENDING'
    ).select_related('user', 'slot', 'slot__lapangan').order_by('-tanggal_booking')
    
    context = {
        'pending_bookings': pending_bookings,
    }
    return render(request, 'admin_dashboard/booking_pending_list.html', context)


@pemilik_required
def booking_approve(request, pk):
    """Approve booking (PENDING → PAID, slot jadi BOOKED)"""
    booking = get_object_or_404(
        Booking, 
        pk=pk, 
        slot__lapangan__pengelola=request.user.profile,
        status_pembayaran='PENDING'
    )
    
    if request.method == 'POST':
        try:
            # Update status booking jadi PAID
            booking.status_pembayaran = 'PAID'
            booking.save()
            
            # Update slot jadi BOOKED (is_available = False)
            slot = booking.slot
            slot.is_available = False
            slot.pending_booking = None  # Clear pending
            slot.save()
            
            messages.success(request, f'Booking #{booking.id} berhasil di-approve!')
            return redirect('admin_dashboard:booking_pending')
            
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
    
    context = {
        'booking': booking,
    }
    return render(request, 'admin_dashboard/booking_approve_confirm.html', context)


@pemilik_required
def booking_reject(request, pk):
    """Reject booking (PENDING → CANCELLED, slot jadi AVAILABLE)"""
    booking = get_object_or_404(
        Booking, 
        pk=pk, 
        slot__lapangan__pengelola=request.user.profile,
        status_pembayaran='PENDING'
    )
    
    if request.method == 'POST':
        try:
            # Update status booking jadi CANCELLED
            booking.status_pembayaran = 'CANCELLED'
            booking.save()
            
            # Update slot jadi AVAILABLE lagi
            slot = booking.slot
            slot.is_available = True
            slot.pending_booking = None  # Clear pending
            slot.save()
            
            messages.success(request, f'Booking #{booking.id} berhasil ditolak!')
            return redirect('admin_dashboard:booking_pending')
            
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
    
    context = {
        'booking': booking,
    }
    return render(request, 'admin_dashboard/booking_reject_confirm.html', context)


@pemilik_required
def transaksi_list(request):
    """Menampilkan riwayat transaksi (PAID & CANCELLED)"""
    status_filter = request.GET.get('status', '')
    
    # Filter transaksi untuk lapangan milik pemilik yang login
    transaksi = Booking.objects.filter(
        slot__lapangan__pengelola=request.user.profile
    ).exclude(
        status_pembayaran='PENDING'  # Exclude yang masih pending
    ).select_related('user', 'slot', 'slot__lapangan').order_by('-tanggal_booking')
    
    if status_filter:
        transaksi = transaksi.filter(status_pembayaran=status_filter)
    
    context = {
        'transaksi': transaksi,
        'status_filter': status_filter,
    }
    return render(request, 'admin_dashboard/transaksi_list.html', context)


@pemilik_required
def booking_sessions_list(request):
    """Menampilkan dan mengelola booking sessions (SlotTersedia)"""
    # Filter lapangan milik pemilik yang login
    lapangan_list = Lapangan.objects.filter(pengelola=request.user.profile)
    
    # Filter berdasarkan lapangan yang dipilih
    selected_lapangan_id = request.GET.get('lapangan_id')
    selected_date_str = request.GET.get('date')
    
    # Tentukan lapangan yang dipilih
    if selected_lapangan_id:
        selected_lapangan = get_object_or_404(lapangan_list, pk=selected_lapangan_id)
    else:
        selected_lapangan = lapangan_list.first() if lapangan_list.exists() else None
    
    # Tentukan tanggal
    if selected_date_str:
        try:
            selected_date = date.fromisoformat(selected_date_str)
        except (ValueError, TypeError):
            selected_date = date.today()
    else:
        selected_date = date.today()
    
    # Ambil slots untuk lapangan dan tanggal yang dipilih
    slots = []
    if selected_lapangan:
        slots = SlotTersedia.objects.filter(
            lapangan=selected_lapangan,
            tanggal=selected_date
        ).order_by('jam_mulai').select_related('pending_booking')
    
    context = {
        'lapangan_list': lapangan_list,
        'selected_lapangan': selected_lapangan,
        'selected_date': selected_date,
        'selected_date_str': selected_date.strftime('%Y-%m-%d'),
        'slots': slots,
    }
    return render(request, 'admin_dashboard/booking_sessions_list.html', context)


@pemilik_required
def booking_sessions_create(request):
    """Membuat booking sessions (slots) untuk lapangan tertentu"""
    if request.method == 'POST':
        try:
            lapangan_id = request.POST.get('lapangan_id')
            start_date_str = request.POST.get('start_date')
            end_date_str = request.POST.get('end_date')
            jam_mulai_str = request.POST.get('jam_mulai')
            jam_akhir_str = request.POST.get('jam_akhir')
            
            # Validasi lapangan
            lapangan = get_object_or_404(
                Lapangan, 
                pk=lapangan_id, 
                pengelola=request.user.profile
            )
            
            # Parse tanggal
            start_date = date.fromisoformat(start_date_str)
            end_date = date.fromisoformat(end_date_str)
            
            # Parse waktu
            jam_mulai = time.fromisoformat(jam_mulai_str)
            jam_akhir = time.fromisoformat(jam_akhir_str)
            
            # Validasi
            if end_date < start_date:
                messages.error(request, 'Tanggal akhir tidak boleh lebih awal dari tanggal mulai!')
                return redirect('admin_dashboard:booking_sessions_create')
            
            if jam_akhir <= jam_mulai:
                messages.error(request, 'Jam akhir harus lebih besar dari jam mulai!')
                return redirect('admin_dashboard:booking_sessions_create')
            
            # Buat slots
            created_count = 0
            current_date = start_date
            
            while current_date <= end_date:
                # Cek apakah slot sudah ada
                existing = SlotTersedia.objects.filter(
                    lapangan=lapangan,
                    tanggal=current_date,
                    jam_mulai=jam_mulai
                ).exists()
                
                if not existing:
                    SlotTersedia.objects.create(
                        lapangan=lapangan,
                        tanggal=current_date,
                        jam_mulai=jam_mulai,
                        jam_akhir=jam_akhir,
                        is_available=True
                    )
                    created_count += 1
                
                current_date += timedelta(days=1)
            
            messages.success(request, f'Berhasil membuat {created_count} booking session!')
            return redirect('admin_dashboard:booking_sessions_list')
            
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
    
    # GET request - tampilkan form
    lapangan_list = Lapangan.objects.filter(pengelola=request.user.profile)
    
    context = {
        'lapangan_list': lapangan_list,
        'today': date.today().strftime('%Y-%m-%d'),
    }
    return render(request, 'admin_dashboard/booking_sessions_create.html', context)


@pemilik_required
def booking_session_delete(request, pk):
    """Hapus booking session tertentu"""
    slot = get_object_or_404(
        SlotTersedia, 
        pk=pk, 
        lapangan__pengelola=request.user.profile
    )
    
    if request.method == 'POST':
        # Cek apakah slot sudah dibooking
        if not slot.is_available or slot.pending_booking:
            messages.error(request, 'Tidak dapat menghapus slot yang sudah dibooking!')
            return redirect('admin_dashboard:booking_sessions_list')
        
        slot.delete()
        messages.success(request, 'Booking session berhasil dihapus!')
        return redirect('admin_dashboard:booking_sessions_list')
    
    context = {'slot': slot}
    return render(request, 'admin_dashboard/booking_session_confirm_delete.html', context)