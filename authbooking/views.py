from django.shortcuts import redirect, render
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CustomUserCreationForm 
from .models import Profile 

# --- VIEWS AUTHENTIKASI ---

def register_user(request):
    """Menangani proses registrasi user baru dengan pilihan Role."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST) 
        
        if form.is_valid():
            user = form.save()
            
            # PERBAIKAN: Cek apakah Profile sudah ada, kalau belum buat
            if not hasattr(user, 'profile'):
                Profile.objects.create(
                    user=user,
                    role=form.cleaned_data['role'],
                    nomor_rekening=form.cleaned_data.get('nomor_rekening', ''),
                    nomor_whatsapp=form.cleaned_data.get('nomor_whatsapp', '')
                )
            
            login(request, user)
            messages.success(request, f"Akun {user.username} berhasil dibuat! Role: {user.profile.get_role_display()}.")
            
            # REDIRECT BERDASARKAN ROLE
            if user.profile.role == 'PEMILIK':
                return redirect('/dashboard/')  # Ke Admin Dashboard
            else:  # PENYEWA
                return redirect('/')  # Ke Landing Page
        else:
            messages.error(request, "Registrasi gagal. Mohon periksa input Anda.")
    else:
        form = CustomUserCreationForm()

    context = {
        'form': form,
        'show_navbar': False
    }
    return render(request, 'register.html', context)


def login_user(request):
    """Menangani proses login user dan redirect berdasarkan role."""
    # Hapus semua pesan lama biar ga numpuk
    storage = messages.get_messages(request)
    storage.used = True
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST) 

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Selamat datang kembali, {user.username}.")
            
            # REDIRECT BERDASARKAN ROLE
            if user.profile.role == 'PEMILIK':
                return redirect('/dashboard/')  # Ke Admin Dashboard
            else:  # PENYEWA
                # Cek apakah ada 'next' parameter untuk redirect setelah login
                next_url = request.GET.get('next', '/')
                return redirect(next_url)
    else:
        form = AuthenticationForm(request)
    
    context = {
        'form': form,
        'show_navbar': False,
        'next': request.GET.get('next', '') 
    }
    return render(request, 'login.html', context)


def logout_user(request):
    """Menghapus sesi user dan mengarahkan kembali ke halaman utama."""
    logout(request)
    messages.info(request, "Anda telah berhasil logout.")
    return redirect('/')