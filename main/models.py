import uuid
from django.db import models

class Community(models.Model):
    CATEGORY_CHOICES = [
        ('padel', 'Padel'),
        ('futsal', 'Futsal'),
        ('bulutangkis', 'Bulutangkis'),
        ('basket', 'Basket'),
    ]

    community_name = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    member_count = models.IntegerField(default=0)
    max_member = models.IntegerField()
    contact_person_name = models.CharField(max_length=30)
    sports_type = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='futsal')
    contact_phone = models.CharField(max_length=20)
    community_image = models.ImageField(upload_to='community_images/', null=True, blank=True)
    date_added = models.DateField(auto_now_add=True)