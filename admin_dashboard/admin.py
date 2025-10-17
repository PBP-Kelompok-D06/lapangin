from django.contrib import admin
from .models import Lapangan, VarianLapangan, WarnaLapangan, KategoriLapangan, GaleriLapangan

@admin.register(Lapangan)
class LapanganAdmin(admin.ModelAdmin):
    list_display = ['nama', 'jenis', 'lokasi', 'harga_per_jam', 'pemilik', 'is_active']
    list_filter = ['jenis', 'is_active']
    search_fields = ['nama', 'lokasi']
    list_editable = ['is_active']

@admin.register(VarianLapangan)
class VarianLapanganAdmin(admin.ModelAdmin):
    list_display = ['lapangan', 'ukuran', 'stock']
    list_filter = ['ukuran']

@admin.register(WarnaLapangan)
class WarnaLapanganAdmin(admin.ModelAdmin):
    list_display = ['lapangan', 'nama_warna', 'kode_hex']

@admin.register(KategoriLapangan)
class KategoriLapanganAdmin(admin.ModelAdmin):
    list_display = ['lapangan', 'nama_kategori']

@admin.register(GaleriLapangan)
class GaleriLapanganAdmin(admin.ModelAdmin):
    list_display = ['lapangan', 'caption', 'tanggal_upload']
    list_filter = ['tanggal_upload']