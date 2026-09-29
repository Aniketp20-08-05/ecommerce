from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('consumer', 'Consumer'),
        ('retailer', 'Retailer'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='consumer')

    def __str__(self):
        return f"{self.user.username} - {self.role}"
