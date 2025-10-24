# pbp-kelompok-d06/lapangin/lapangin-feat-admin-dashboard/booking/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from .models import SlotTersedia, Booking, Lapangan
from datetime import date, timedelta, datetime # Pastikan datetime diimpor
from django.contrib import messages
from django.utils import timezone
import json
import os # Tetap impor os jika diperlukan di tempat lain
from django.conf import settings # Tetap impor settings jika diperlukan di tempat lain
from django.db.models import Q

# --- TAMBAHAN IMPORT YANG BENAR ---
from django.templatetags.static import static
from django.contrib.staticfiles.finders import find
# ----------------------------------

def show_booking_page(request):

    all_lapangan = Lapangan.objects.all().order_by('nama_lapangan')

    # 1. Ambil ID Lapangan dan Tanggal dari Query GET
    lapangan_id_filter = request.GET.get('lapangan_id')
    selected_date_str = request.GET.get('date')

    # Tentukan Lapangan yang akan ditampilkan
    if lapangan_id_filter:
        lapangan_terpilih = get_object_or_404(all_lapangan, pk=lapangan_id_filter)
    else:
        lapangan_terpilih = all_lapangan.first()

    # --- LOGIKA PRIORITAS GAMBAR HERO YANG DIPERBAIKI ---
    hero_image_url = static('images/lapangan_default.jpg') # Default image URL
    static_specific_path = None # Path relatif static spesifik

    if lapangan_terpilih:
        # Prioritas 1: Cek foto_utama dari Media
        if lapangan_terpilih.foto_utama:
            hero_image_url = lapangan_terpilih.foto_utama.url # Langsung pakai URL dari media
            lapangan_terpilih.static_image_path = None # Tidak pakai static jika media ada
        else:
            # Prioritas 2: Cek static spesifik (png/jpg) menggunakan find()
            possible_static_path_png = f'images/lapangan{lapangan_terpilih.pk}.png'
            possible_static_path_jpg = f'images/lapangan{lapangan_terpilih.pk}.jpg'

            if find(possible_static_path_png):
                static_specific_path = possible_static_path_png
                hero_image_url = static(static_specific_path) # Buat URL lengkap dengan static()
            elif find(possible_static_path_jpg):
                static_specific_path = possible_static_path_jpg
                hero_image_url = static(static_specific_path) # Buat URL lengkap dengan static()
            # Jika tidak ada media dan tidak ada static spesifik, default (di atas) akan digunakan.

        # Simpan path relatif static (atau None) di objek untuk konsistensi (opsional)
        lapangan_terpilih.static_image_path = static_specific_path

    # --- Akhir Logika Gambar ---

    if not lapangan_terpilih:
        messages.error(request, 'Tidak ada data lapangan di database.')
        # Sebaiknya redirect ke halaman lain atau tampilkan pesan error
        # return redirect('main:show_landing_page') # Contoh
        return render(request, 'booking.html', {'error': 'Tidak ada lapangan.', 'show_navbar': True}) # Tampilkan pesan di template


    # 2. Tentukan Tanggal Mulai Filter
    if selected_date_str:
        try:
            filter_date = date.fromisoformat(selected_date_str)
        except (ValueError, TypeError):
            filter_date = date.today()
    else:
        filter_date = date.today()

    # Tentukan rentang 7 hari
    date_list = [filter_date + timedelta(days=i) for i in range(7)]

    # 3. Ambil slot yang relevan
    available_slots_queryset = SlotTersedia.objects.select_related('pending_booking').filter(
        lapangan=lapangan_terpilih,
        tanggal__in=date_list,
    ).order_by('tanggal', 'jam_mulai')

    # Re-organisasi slots
    slots_by_date = {}
    for slot_date in date_list:
        slots = list(available_slots_queryset.filter(tanggal=slot_date))
        for slot in slots:
            slot.display_status = 'AVAILABLE'
            if not slot.is_available:
                slot.display_status = 'BOOKED'
            elif slot.pending_booking is not None:
                slot.display_status = 'PENDING'
        slots_by_date[slot_date] = slots

    context = {
        'lapangan_terpilih': lapangan_terpilih,
        'all_lapangan': all_lapangan,
        'filter_date_str': filter_date.strftime('%Y-%m-%d'),
        'date_list': date_list,
        'slots_by_date': slots_by_date,
        'today': date.today(),
        'hero_image_url': hero_image_url, # <-- URL gambar hero yang sudah benar
        'show_navbar': True,
    }

    return render(request, 'booking.html', context)


# 2. create_booking: Memproses permintaan booking dari AJAX (Form Input Wajib)
@csrf_protect
@login_required
def create_booking(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'message': 'Anda harus login untuk booking.'}, status=403)

        try:
            data = json.loads(request.body)
            slot_id = data.get('slot_id')
            slot = get_object_or_404(SlotTersedia, pk=slot_id)

            # --- TAMBAHAN VALIDASI: Cek ketersediaan slot sebelum membuat ---
            if not slot.is_available or slot.pending_booking:
                 return JsonResponse({'success': False, 'message': 'Maaf, slot ini baru saja dibooking.'}, status=409) # 409 Conflict

            # Hitung total pembayaran
            raw_price = slot.lapangan.harga_per_jam
            total_bayar = raw_price if raw_price is not None else 0

            booking = Booking.objects.create(
                user=request.user,
                slot=slot,
                tanggal_booking=timezone.now(),
                total_bayar=total_bayar,
                status_pembayaran='PENDING'
            )

            # Update Slot untuk menandai sedang pending
            slot.pending_booking = booking
            slot.is_available = True # Biarkan available True dulu, status PENDING ditandai oleh pending_booking FK
            slot.save()

            return JsonResponse({
                'success': True,
                'booking_id': booking.id,
                'message': 'Request berhasil dibuat. Lanjut ke pembayaran.'
            }, status=200)

        except SlotTersedia.DoesNotExist:
             return JsonResponse({'success': False, 'message': 'Slot tidak ditemukan.'}, status=404)
        except Exception as e:
            # Log error di server
            print(f"Error creating booking: {e}")
            return JsonResponse({'success': False, 'message': 'Terjadi kesalahan di server. Coba lagi nanti.'}, status=500)

    return JsonResponse({'message': 'Metode tidak diizinkan.'}, status=405)


# View AJAX untuk Polling Status Slot
def check_slot_status(request):
    lapangan_id = request.GET.get('lapangan_id')

    if not lapangan_id:
        return JsonResponse({'error': 'Lapangan ID is required'}, status=400)

    try:
        # Cukup filter berdasarkan ID, tidak perlu get object utuh
        slots_data = SlotTersedia.objects.filter(
            lapangan_id=lapangan_id # Filter langsung pakai ID
        ).values(
            'id',
            'is_available',
            'pending_booking__id'
        )

        response_data = []
        for slot in slots_data:
            status = 'AVAILABLE'
            # Logika status harus konsisten dengan create_booking dan show_booking_page
            if not slot['is_available']: # Jika admin sudah approve/reject
                # Cek apakah ada booking PAID untuk slot ini (meskipun jarang terjadi race condition di sini)
                 if Booking.objects.filter(slot_id=slot['id'], status_pembayaran='PAID').exists():
                      status = 'BOOKED'
                 else: # Jika tidak available tapi tidak PAID, kemungkinan CANCELLED atau error data
                      status = 'AVAILABLE' # Anggap saja available jika tidak terkonfirmasi booked
            elif slot['pending_booking__id'] is not None:
                # Cek apakah booking pending masih valid (belum timeout/dibatalkan)
                try:
                    pending_book = Booking.objects.get(pk=slot['pending_booking__id'])
                    timeout_duration = timedelta(minutes=5)
                    if pending_book.status_pembayaran == 'PENDING' and timezone.now() <= pending_book.tanggal_booking + timeout_duration:
                        status = 'PENDING'
                    # else: biarkan status AVAILABLE jika booking pending sudah tidak valid
                except Booking.DoesNotExist:
                    # Jika booking pending tidak ditemukan (misal dihapus), anggap slot available
                    pass # Biarkan status AVAILABLE

            response_data.append({
                'id': slot['id'],
                'status': status
            })

        return JsonResponse(response_data, safe=False)

    except Lapangan.DoesNotExist: # Perlu diimpor jika ingin catch ini
        return JsonResponse({'error': 'Lapangan not found'}, status=404)
    except Exception as e:
        print(f"Error polling status: {e}") # Log error
        return JsonResponse({'error': 'Internal server error during polling'}, status=500)


# 3. show_payment_page: Menampilkan instruksi pembayaran
@login_required
def show_payment_page(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)

    if booking.user != request.user:
        messages.error(request, "Anda tidak memiliki akses ke pemesanan ini.")
        return redirect('booking:show_booking_page')

    timeout_duration = timedelta(minutes=5)
    time_to_expire_ms = None # Default jika tidak pending

    if booking.status_pembayaran == 'PENDING':
        timeout_time = booking.tanggal_booking + timeout_duration

        if timezone.now() > timeout_time:
            # Logic Pembatalan Otomatis (pastikan konsisten)
            slot_terkait = booking.slot
            # Hanya set pending_booking=None jika slot masih menunjuk ke booking ini
            if slot_terkait and slot_terkait.pending_booking_id == booking.id:
                slot_terkait.pending_booking = None
                slot_terkait.is_available = True # Pastikan available kembali True
                slot_terkait.save()
            booking.status_pembayaran = 'CANCELLED'
            booking.save()

            storage = messages.get_messages(request)
            storage.used = True
            if request.user.is_authenticated:
                messages.error(request, "Waktu pembayaran (5 menit) telah habis. Pemesanan dibatalkan.")
            return redirect('booking:show_booking_page') # Redirect setelah batal

        time_to_expire_ms = int(timeout_time.timestamp() * 1000)

    # Ambil data pemilik lapangan (pastikan pengelola ada)
    no_rekening = 'Tidak tersedia'
    contact_whatsapp = 'Tidak tersedia'
    if booking.slot.lapangan.pengelola:
        pemilik_profile = booking.slot.lapangan.pengelola
        no_rekening = pemilik_profile.nomor_rekening or 'Tidak tersedia'
        contact_whatsapp = pemilik_profile.nomor_whatsapp or 'Tidak tersedia'
        # Hapus '+' dari nomor WA untuk link wa.me
        if contact_whatsapp.startswith('+'):
            contact_whatsapp = contact_whatsapp[1:]


    context = {
        'booking': booking,
        'no_rekening': no_rekening,
        'contact_whatsapp': contact_whatsapp,
        'time_to_expire_ms': time_to_expire_ms,
        'show_navbar': True,
    }

    return render(request, 'payment_detail.html', context)


@login_required
def my_bookings(request):
    # Ambil semua booking user, urutkan berdasarkan tanggal booking terbaru
    # Status PENDING juga ditampilkan agar user tahu mana yang perlu dibayar/dikonfirmasi
    bookings = (
        Booking.objects
        .select_related('slot__lapangan')
        .filter(user=request.user)
        .order_by('-tanggal_booking') # Urutkan dari yang terbaru
    )

    context = {
        'bookings': bookings,
        'show_navbar': True,
    }
    return render(request, 'my_bookings.html', context) # Pastikan template my_bookings.html ada