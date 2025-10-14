from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from .models import SlotTersedia, Booking, Lapangan
from datetime import date, timedelta
from django.views.decorators.csrf import csrf_exempt 
import json 
from django.db.models import Q 

def show_booking_page(request):
    
    all_lapangan = Lapangan.objects.all().order_by('nama_lapangan')
    
    # 1. Ambil ID Lapangan dan Tanggal dari Query GET
    lapangan_id_filter = request.GET.get('lapangan_id')
    selected_date_str = request.GET.get('date') # Ambil string tanggal dari URL
    
    # Tentukan Lapangan yang akan ditampilkan
    if lapangan_id_filter:
        lapangan_terpilih = get_object_or_404(all_lapangan, pk=lapangan_id_filter)
    else:
        lapangan_terpilih = all_lapangan.first()
    
    if not lapangan_terpilih:
        return render(request, 'booking.html', {'error': 'Tidak ada data lapangan di database.'})
        
    # 2. Tentukan Tanggal Mulai Filter (Wajib Kuat)
    if selected_date_str:
        # Jika nilai date ada di URL (meskipun kosong/invalid)
        try:
            filter_date = date.fromisoformat(selected_date_str)
        except (ValueError, TypeError): 
            filter_date = date.today() # Kembali ke hari ini jika parsing gagal
    else:
        # Jika parameter date tidak ada di URL sama sekali
        filter_date = date.today()

    # Tentukan rentang 7 hari
    date_list = [filter_date + timedelta(days=i) for i in range(7)]
    
    # 3. Ambil slot yang relevan
    available_slots_queryset = SlotTersedia.objects.filter(
        lapangan=lapangan_terpilih,
        tanggal__in=date_list,
    ).order_by('tanggal', 'jam_mulai')

    # Re-organisasi slots ke dalam dictionary {tanggal: [slot1, slot2, ...]}
    slots_by_date = {}
    for slot_date in date_list:
        slots_by_date[slot_date] = list(
            available_slots_queryset.filter(tanggal=slot_date)
        )
        
    context = {
        'lapangan_terpilih': lapangan_terpilih,
        'all_lapangan': all_lapangan,
        'filter_date_str': filter_date.strftime('%Y-%m-%d'),
        'date_list': date_list,
        'slots_by_date': slots_by_date,
        'today': date.today(),
    }
    
    return render(request, 'booking.html', context)


# 2. create_booking: Memproses permintaan booking dari AJAX (Form Input Wajib)
@csrf_exempt # Digunakan untuk mempermudah AJAX POST saat development (HATI-HATI di production)
@login_required # Filter Informasi/Login Wajib! Memastikan user terautentikasi
def create_booking(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            # Wajib: Implementasi Filter Informasi (Login)
            return JsonResponse({'message': 'Anda harus login untuk booking.'}, status=403)
        
        try:
            data = json.loads(request.body)
            slot_id = data.get('slot_id')
            
            slot = get_object_or_404(SlotTersedia, pk=slot_id)
            
            # CEK KETERSEDIAAN (Filter Informasi: Tidak bisa booking slot yang sudah di-booking)
            if not slot.is_available:
                return JsonResponse({'message': 'Slot ini sudah dibooking oleh orang lain.'}, status=400)
            
            # TODO: Tambahkan check apakah user sudah punya booking yang statusnya pending
            
            # 1. Ubah status Slot menjadi 'BOOKED'
            slot.is_available = False
            slot.save()
            
            # 2. Hitung total_bayar
            total_bayar = slot.lapangan.harga_per_jam
            
            # 3. Buat objek Booking baru
            booking = Booking.objects.create(
                user=request.user,
                slot=slot,
                tanggal_booking=slot.tanggal,
                total_bayar=total_bayar,
                status_pembayaran='PENDING' 
            )
            
            # Kunci: Mengembalikan ID Booking yang baru dibuat ke client
            return JsonResponse({
                'success': True, 
                'booking_id': booking.id, 
                'message': 'Booking berhasil dibuat. Lanjut ke pembayaran.'
            }, status=200)
            
        except SlotTersedia.DoesNotExist:
            return JsonResponse({'message': 'Slot tidak valid.'}, status=404)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)
            
    return JsonResponse({'message': 'Metode tidak diizinkan.'}, status=405)


# 3. show_payment_page: Menampilkan instruksi pembayaran
@login_required # Filter Informasi/Login Wajib!
# VIEW Halaman Pembayaran (Dipanggil setelah redirect sukses)
def show_payment_page(request, booking_id):
    # Wajib: Filter Informasi (Hanya user pemilik booking yang boleh melihat)
    booking = get_object_or_404(Booking, pk=booking_id)

    if booking.user != request.user:
        # Jika bukan pemilik, redirect atau tampilkan error
        return redirect('booking:show_booking_page')

    context = {
        'booking': booking,
        'no_rekening': '123456789 (BCA a.n. Pengelola Lapang.in)',
        'kontak_person': '0812-xxxx-xxxx (Admin Lapang.in)',
        'contact_whatsapp': '62812xxxxxxxx' 
    }
    return render(request, 'payment_detail.html', context)
