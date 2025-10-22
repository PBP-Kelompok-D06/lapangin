from django.shortcuts import redirect, render
from django.contrib.auth.forms import UserCreationForm,  AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CustomUserCreationForm 

# --- VIEWS AUTHENTIKASI ---

def register_user(request):
    """Menangani proses registrasi user baru dengan pilihan Role."""
    if request.method == 'POST':
        # Menggunakan Form kustom yang menangani field Role
        form = CustomUserCreationForm(request.POST) 
        
        if form.is_valid():
            user = form.save()
            login(request, user) 
            # Menggunakan f-string untuk menampilkan Role (Sesuai Logic Model Anda)
            messages.success(request, f"Akun {user.username} berhasil dibuat! Role: {user.profile.get_role_display()}.")
            
            # Pakai "/" untuk sementara karena page home belum dibuat, nanti ganti ke "home"
            return redirect('/')
        else:
            messages.error(request, "Registrasi gagal. Mohon periksa input Anda.")
    else:
        form = CustomUserCreationForm()

    context = {
        'form': form,
        'show_navbar': False # Untuk styling halaman penuh
    }
    # Perbaikan Path Template: Menggunakan path yang benar 'register.html'
    return render(request, 'register.html', context)


def login_user(request):
    """Menangani proses login user dan redirect ke halaman 'next'."""
    # Hapus semua pesan lama biar ga numpuk
    storage = messages.get_messages(request)
    storage.used = True  # tandai semua pesan sudah 'terbaca'
    
    if request.method == 'POST':
        # AuthenticationForm harus selalu disetel ke None saat POST (kecuali saat binding)
        form = AuthenticationForm(request, data=request.POST) 

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Selamat datang kembali, {user.username}.")
            
            # Perbaikan: Mengambil URL 'next' untuk redirect setelah login
            # Jika user datang dari /accounts/login/?next=/booking/create/, ia akan kembali ke sana.
            next_url = request.GET.get('next', '/') # Pakai "/" untuk sementara karena page home belum dibuat, nanti ganti ke "home"
            return redirect(next_url)

    else:
        # Menangani GET request
        form = AuthenticationForm(request)
    
    # Tambahkan 'next' ke context agar form action tetap mengarah ke halaman yang benar
    context = {
        'form': form,
        'show_navbar': False,
        'next': request.GET.get('next', '') 
    }
    # Perbaikan Path Template: Menggunakan path yang benar 'login.html'
    return render(request, 'login.html', context)


def logout_user(request):
    """Menghapus sesi user dan mengarahkan kembali ke halaman utama."""
    logout(request)
    messages.info(request, "Anda telah berhasil logout.")
    
    # Pakai "/" untuk sementara karena page home belum dibuat, nanti ganti ke "home"
    return redirect('/')