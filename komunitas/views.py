from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Komunitas, RequestKomunitas

def is_admin(user):
    return user.is_staff or user.groups.filter(name='Admin').exists()

@login_required
@user_passes_test(is_admin)
def komunitas_list(request):
    """Daftar komunitas untuk admin"""
    jenis_filter = request.GET.get('jenis', '')
    lokasi_filter = request.GET.get('lokasi', '')
    
    komunitas_list = Komunitas.objects.filter(dibuat_oleh=request.user)
    
    if jenis_filter:
        komunitas_list = komunitas_list.filter(jenis_olahraga=jenis_filter)
    if lokasi_filter:
        komunitas_list = komunitas_list.filter(lokasi__icontains=lokasi_filter)
    
    context = {
        'komunitas_list': komunitas_list,
    }
    return render(request, 'komunitas/komunitas_list.html', context)


@login_required
@user_passes_test(is_admin)
def komunitas_create(request):
    """Form membuat komunitas baru"""
    if request.method == 'POST':
        try:
            komunitas = Komunitas.objects.create(
                nama=request.POST.get('nama'),
                deskripsi=request.POST.get('deskripsi'),
                lokasi=request.POST.get('lokasi'),
                jenis_olahraga=request.POST.get('jenis_olahraga'),
                link_grup=request.POST.get('link_grup', ''),
                dibuat_oleh=request.user
            )
            
            if request.FILES.get('foto'):
                komunitas.foto = request.FILES['foto']
                komunitas.save()
            
            messages.success(request, 'Komunitas berhasil dibuat!')
            return redirect('komunitas:komunitas_list')
            
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
    
    return render(request, 'komunitas/komunitas_form.html')


@login_required
@user_passes_test(is_admin)
def komunitas_edit(request, pk):
    """Edit komunitas"""
    komunitas = get_object_or_404(Komunitas, pk=pk, dibuat_oleh=request.user)
    
    if request.method == 'POST':
        try:
            komunitas.nama = request.POST.get('nama')
            komunitas.deskripsi = request.POST.get('deskripsi')
            komunitas.lokasi = request.POST.get('lokasi')
            komunitas.jenis_olahraga = request.POST.get('jenis_olahraga')
            komunitas.link_grup = request.POST.get('link_grup', '')
            
            if request.FILES.get('foto'):
                komunitas.foto = request.FILES['foto']
            
            komunitas.save()
            
            messages.success(request, 'Komunitas berhasil diupdate!')
            return redirect('komunitas:komunitas_list')
            
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
    
    context = {'komunitas': komunitas}
    return render(request, 'komunitas/komunitas_form.html', context)


@login_required
@user_passes_test(is_admin)
def komunitas_delete(request, pk):
    """Hapus komunitas"""
    komunitas = get_object_or_404(Komunitas, pk=pk, dibuat_oleh=request.user)
    
    if request.method == 'POST':
        komunitas.delete()
        messages.success(request, 'Komunitas berhasil dihapus!')
        return redirect('komunitas:komunitas_list')
    
    return render(request, 'komunitas/komunitas_confirm_delete.html', {'komunitas': komunitas})


@login_required
@user_passes_test(is_admin)
def request_komunitas_list(request):
    """Daftar request komunitas dari member"""
    requests = RequestKomunitas.objects.filter(status='pending')
    
    context = {'requests': requests}
    return render(request, 'komunitas/request_list.html', context)


@login_required
@user_passes_test(is_admin)
def request_komunitas_approve(request, pk):
    """Approve request dan buat komunitas baru"""
    req = get_object_or_404(RequestKomunitas, pk=pk)
    
    if request.method == 'POST':
        # Buat komunitas baru dari request
        Komunitas.objects.create(
            nama=req.nama_komunitas,
            deskripsi=req.deskripsi,
            lokasi=req.lokasi_preferensi,
            jenis_olahraga=req.jenis_olahraga,
            dibuat_oleh=request.user
        )
        
        # Update status request
        req.status = 'approved'
        req.catatan_admin = request.POST.get('catatan', '')
        req.save()
        
        messages.success(request, 'Request berhasil diapprove dan komunitas telah dibuat!')
        return redirect('komunitas:request_list')
    
    return render(request, 'komunitas/request_approve.html', {'request': req})


@login_required
@user_passes_test(is_admin)
def request_komunitas_reject(request, pk):
    """Reject request komunitas"""
    req = get_object_or_404(RequestKomunitas, pk=pk)
    
    if request.method == 'POST':
        req.status = 'rejected'
        req.catatan_admin = request.POST.get('catatan', '')
        req.save()
        
        messages.success(request, 'Request berhasil ditolak!')
        return redirect('komunitas:request_list')
    
    return render(request, 'komunitas/request_reject.html', {'request': req})