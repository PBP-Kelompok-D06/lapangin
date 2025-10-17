from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Profile # Import Model Profile yang baru dibuat

class CustomUserCreationForm(UserCreationForm):
    # 1. Menambahkan field Role ke form registrasi
    role = forms.ChoiceField(
        choices=Profile.ROLES,
        label="Daftar Sebagai",
        initial='PENYEWA',
        widget=forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-md'})
    )

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('role',) # Menambahkan field 'role' ke form

    # --- KODE BARU UNTUK MENAMBAH STYLE KE FIELD BAWAAN ---
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Class styling Tailwind yang kita inginkan (w-full, border, focus, dll.)
        tailwind_classes = 'w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:border-[#839556] transition-colors'
        
        # Iterasi melalui field bawaan (username, password1, password2)
        for field_name in self.fields:
            # Pastikan kita tidak menimpa field Role yang sudah di-style di atas
            if field_name != 'role':
                self.fields[field_name].widget.attrs.update({
                    'class': tailwind_classes
                })
        
        # Atur placeholder di sini (opsional)
        self.fields['username'].widget.attrs['placeholder'] = 'Enter your username'
        self.fields['password1'].widget.attrs['placeholder'] = 'Enter your password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm your password'
    # -----------------------------------------------------------------

    # 2. Logic menyimpan Role setelah user berhasil dibuat
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # KUNCI: Membuat objek Profile dan menyimpan Role yang dipilih
            role = self.cleaned_data.get('role')
            Profile.objects.create(user=user, role=role)
        return user