from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_guest = models.BooleanField(default=False)  # Neues Feld hinzufügen
    created_at = models.DateTimeField(auto_now_add=True)  # Optional: für spätere Bereinigung
    
    def __str__(self):
        return f"{self.user.username} ({'Gast' if self.is_guest else 'Benutzer'})"