from django.db import models
from django.contrib.auth.models import User

class Komunitas(models.Model):
    JENIS_CHOICES = [
        ('futsal', 'Futsal'),
        ('basket', 'Basket'),
        ('badminton', 'Badminton'),
    ]
    
    nama = models.CharField(max_length=200)
    deskripsi = models.TextField()
    lokasi = models.CharField(max_length=200)
    jenis_olahraga = models.CharField(max_length=50, choices=JENIS_CHOICES)
    foto = models.ImageField(upload_to='komunitas/', null=True, blank=True)
    link_grup = models.URLField(max_length=500, blank=True)
    jumlah_anggota = models.IntegerField(default=0)
    tanggal_dibuat = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    dibuat_oleh = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Komunitas'
        ordering = ['-tanggal_dibuat']

    def __str__(self):
        return self.nama


class RequestKomunitas(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    pemohon = models.ForeignKey(User, on_delete=models.CASCADE)
    nama_komunitas = models.CharField(max_length=200)
    deskripsi = models.TextField()
    jenis_olahraga = models.CharField(max_length=50)
    lokasi_preferensi = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    tanggal_request = models.DateTimeField(auto_now_add=True)
    catatan_admin = models.TextField(blank=True)

    class Meta:
        ordering = ['-tanggal_request']

    def __str__(self):
        return f"{self.nama_komunitas} - {self.pemohon.username}"
