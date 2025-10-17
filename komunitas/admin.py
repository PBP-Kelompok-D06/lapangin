from django.contrib import admin
from .models import Komunitas, RequestKomunitas

@admin.register(Komunitas)
class KomunitasAdmin(admin.ModelAdmin):
    list_display = ['nama', 'jenis_olahraga', 'lokasi', 'jumlah_anggota', 'dibuat_oleh', 'is_active']
    list_filter = ['jenis_olahraga', 'is_active']
    search_fields = ['nama', 'lokasi']
    list_editable = ['is_active']

@admin.register(RequestKomunitas)
class RequestKomunitasAdmin(admin.ModelAdmin):
    list_display = ['nama_komunitas', 'jenis_olahraga', 'pemohon', 'status', 'tanggal_request']
    list_filter = ['status', 'jenis_olahraga']
    search_fields = ['nama_komunitas', 'pemohon__username']
    list_editable = ['status']