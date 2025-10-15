from django.db import models
from django.contrib.auth.models import User
from booking.models import Field

class Review (models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.field.name} - Rating: {self.rating}"

# Create your models here.
