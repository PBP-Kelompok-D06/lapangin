from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()

class Lapangan(models.Model):
    nama = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    deskripsi = models.TextField(blank=True)
    harga_per_jam = models.PositiveIntegerField(default=0)
    gambar = models.ImageField(upload_to='lapangan/')
    fasilitas = models.CharField(max_length=200, blank=True)
    dibuat = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nama)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nama

    def avg_rating(self):
        reviews = self.review_set.all()
        if not reviews:
            return 0
        return round(sum(r.rating for r in reviews) / reviews.count(), 1)


class Review(models.Model):
    lapangan = models.ForeignKey(Lapangan, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    komentar = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    dibuat = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.lapangan.nama}"
