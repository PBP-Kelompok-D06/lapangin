from django.shortcuts import redirect, render
from django.contrib.auth.forms import UserCreationForm,  AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CustomUserCreationForm 


def register_user(request):
    """Menangani proses registrasi user baru dengan pilihan Role."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST) # <-- GUNAKAN FORM KUSTOM BARU
        
        if form.is_valid():
            user = form.save()
            # Setelah berhasil daftar, langsung login
            login(request, user) 
            messages.success(request, f"Akun {user.username} berhasil dibuat! Role: {user.profile.get_role_display()}.")
            return redirect('/')
        else:
            messages.error(request, "Registrasi gagal. Mohon periksa input Anda.")
    else:
        form = CustomUserCreationForm()

    context = {
        'form': form,
        'show_navbar': False}
    return render(request, 'register.html', context)

def login_user(request):
   if request.method == 'POST':
      form = AuthenticationForm(data=request.POST)

      if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/')

   else:
      form = AuthenticationForm(request)
   context = {'form': form,
              'show_navbar': False}
   return render(request, 'login.html', context)

def logout_user(request):
    logout(request)
    return redirect('authbooking:login')
