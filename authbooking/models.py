from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    # Definisi 2 Roles yang Diperlukan
    ROLES = [
        ('USER', 'User (Penyewa)'),
        ('ADMIN', 'Admin (Pemilik Lapangan)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=5, choices=ROLES, default='USER')

    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'