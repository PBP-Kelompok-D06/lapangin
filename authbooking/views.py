from django.shortcuts import redirect, render
from django.contrib.auth.forms import UserCreationForm,  AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
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
            user = form.save(commit=False)
            user.save()

            # Buat Profile baru berdasarkan data dari form
            Profile.objects.create(
                user=user,
                role=form.cleaned_data.get('role'),
                nomor_rekening=form.cleaned_data.get('nomor_rekening'),
                nomor_whatsapp=form.cleaned_data.get('nomor_whatsapp')
            )

            login(request, user)
            messages.success(
                request,
                f"Akun {user.username} berhasil dibuat! Role: {user.profile.get_role_display()}."
            )
            # Redirect berdasarkan role
            profile = Profile.objects.get(user=user)
            if profile.role == 'PEMILIK':
                return redirect('admin_dashboard:dashboard_home') # kalo dia register sebagai PEMILIK diarahin ke dashboard
            else:
                return redirect('/') # kalo dia register sebagai PENYEWA diarahin ke landing page
        else:
            messages.error(request, "Registrasi gagal. Mohon periksa input Anda.")
    else:
        form = CustomUserCreationForm()

    context = {'form': form, 'show_navbar': False}
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
            
            # Redirect berdasarkan role
            try:
                profile = Profile.objects.get(user=user)
            except Profile.DoesNotExist:
                messages.error(request, "Profil Anda belum lengkap. Silakan hubungi admin.")
                return redirect('/')
            
            if profile.role == 'PEMILIK':
                return redirect('admin_dashboard:dashboard_home') # kalo dia register sebagai PEMILIK diarahin ke dashboard
            else:
                # Perbaikan: Mengambil URL 'next' untuk redirect setelah login
                # Jika user datang dari /accounts/login/?next=/booking/create/, ia akan kembali ke sana.
                next_url = request.GET.get('next', '/') # Pakai "/" untuk sementara karena page home belum dibuat, nanti ganti ke "home"
                return redirect(next_url) # kalo dia register sebagai PENYEWA diarahin ke landing page

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