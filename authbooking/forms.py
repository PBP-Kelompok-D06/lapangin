from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=Profile.ROLES, label="Role selection")
    nomor_rekening = forms.CharField(max_length=50, required=False, label="Account number")
    nomor_whatsapp = forms.CharField(max_length=20, required=False, label="WhatsApp number")

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'role', 'nomor_rekening', 'nomor_whatsapp')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ... existing code ...
    
    def clean_nomor_whatsapp(self):
        nomor = self.cleaned_data.get('nomor_whatsapp', '').strip()
        
        # Skip validasi jika kosong (untuk PENYEWA)
        if not nomor:
            return nomor
        
        # Normalisasi nomor
        if nomor.startswith('0'):
            nomor = '+62' + nomor[1:]
        elif not nomor.startswith('+'):
            nomor = '+62' + nomor

        # Validasi format
        nomor_digits = nomor.replace('+', '').replace('62', '', 1)
        if not nomor_digits.isdigit():
            raise forms.ValidationError("Nomor WhatsApp hanya boleh berisi angka setelah tanda '+'.")
        
        if len(nomor) < 10 or len(nomor) > 15:
            raise forms.ValidationError("Nomor WhatsApp tampaknya tidak valid.")
        
        return nomor
    
    # TAMBAHKAN METHOD INI (PENTING!)
    def save(self, commit=True):
        user = super().save(commit=False)
        
        if commit:
            user.save()
            
            # Buat Profile untuk user
            Profile.objects.create(
                user=user,
                role=self.cleaned_data['role'],
                nomor_rekening=self.cleaned_data.get('nomor_rekening', ''),
                nomor_whatsapp=self.cleaned_data.get('nomor_whatsapp', '')
            )
        
        return user