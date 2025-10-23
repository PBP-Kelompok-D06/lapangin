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
        form = CustomUserCreationForm(request.POST) 
        
        if form.is_valid():
            user = form.save()
            login(request, user)  # User sudah login otomatis
        
            role = user.profile.role
            
            if role == 'PEMILIK':
                messages.success(request, f"Akun {user.username} berhasil dibuat sebagai Pemilik Lapangan!")
                return redirect('admin_dashboard:dashboard_home')  # Langsung ke dashboard
            else:  # PENYEWA
                messages.success(request, f"Akun {user.username} berhasil dibuat sebagai Penyewa!")
                return redirect('booking:show_booking_page')  # Ke halaman booking
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
    """Menangani proses login user dan redirect ke halaman 'next'."""
    storage = messages.get_messages(request)
    storage.used = True
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST) 

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Selamat datang kembali, {user.username}.")
            
            # ✅ PERBAIKAN: Redirect berdasarkan role jika tidak ada 'next'
            next_url = request.GET.get('next', '')
            
            if next_url:
                return redirect(next_url)
            
            # Jika tidak ada next, redirect berdasarkan role
            if hasattr(user, 'profile') and user.profile.role == 'PEMILIK':
                return redirect('admin_dashboard:dashboard_home')
            else:
                return redirect('booking:show_booking_page')

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
    
    # ✅ PERBAIKAN: Redirect ke halaman login
    return redirect('authbooking:login')