from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from user_auth_app.models import UserProfile
from datetime import timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Bereinigt alte Gast-Accounts'

    def handle(self, *args, **options):
        cutoff_date = timezone.now() - timedelta(days=7)
        old_guests = UserProfile.objects.filter(
            is_guest=True, 
            created_at__lt=cutoff_date
        )
        
        for profile in old_guests:
            user = profile.user
            self.stdout.write(f"Lösche Gast: {user.username}")
            user.delete()  # Löscht auch das Profil wegen CASCADE
        
        self.stdout.write(f"Bereinigung abgeschlossen. {old_guests.count()} Gast-Accounts wurden gelöscht.")