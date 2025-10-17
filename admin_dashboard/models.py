from django.db import models
from django.contrib.auth.models import User

class Lapangan(models.Model):
    JENIS_CHOICES = [
        ('futsal', 'Futsal'),
        ('basket', 'Basket'),
        ('badminton', 'Badminton'),
    ]
    
    nama = models.CharField(max_length=200)
    jenis = models.CharField(max_length=50, choices=JENIS_CHOICES)
    lokasi = models.CharField(max_length=300)
    harga_per_jam = models.DecimalField(max_digits=10, decimal_places=2)
    deskripsi = models.TextField()
    fasilitas = models.TextField()
    foto_utama = models.ImageField(upload_to='lapangan/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    pemilik = models.ForeignKey(User, on_delete=models.CASCADE)
    tanggal_dibuat = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nama']

    def __str__(self):
        return f"{self.nama} - {self.get_jenis_display()}"


class VarianLapangan(models.Model):
    UKURAN_CHOICES = [
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
    ]
    
    lapangan = models.ForeignKey(Lapangan, on_delete=models.CASCADE, related_name='varian')
    ukuran = models.CharField(max_length=2, choices=UKURAN_CHOICES)
    stock = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.lapangan.nama} - {self.ukuran}"


class WarnaLapangan(models.Model):
    lapangan = models.ForeignKey(Lapangan, on_delete=models.CASCADE, related_name='warna')
    nama_warna = models.CharField(max_length=50)
    kode_hex = models.CharField(max_length=7)

    def __str__(self):
        return f"{self.lapangan.nama} - {self.nama_warna}"


class KategoriLapangan(models.Model):
    lapangan = models.ForeignKey(Lapangan, on_delete=models.CASCADE, related_name='kategori')
    nama_kategori = models.CharField(max_length=100)

    def __str__(self):
        return self.nama_kategori


class GaleriLapangan(models.Model):
    lapangan = models.ForeignKey(Lapangan, on_delete=models.CASCADE, related_name='galeri')
    foto = models.ImageField(upload_to='galeri_lapangan/')
    caption = models.CharField(max_length=200, blank=True)
    tanggal_upload = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-tanggal_upload']

    def __str__(self):
        return f"Foto {self.lapangan.nama}"