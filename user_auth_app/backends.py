from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

class EmailOrUsernameModelBackend(ModelBackend):
    """
    Authentifizierung mit E-Mail oder Benutzername
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        
        # Versuche den Benutzer anhand des Benutzernamens oder der E-Mail zu finden
        try:
            # Verwende Q-Objekte für OR-Abfrage (Benutzername ODER E-Mail)
            user = UserModel.objects.filter(
                Q(username__iexact=username) | Q(email__iexact=username)
            ).first()
            
            # Prüfe das Passwort, wenn ein Benutzer gefunden wurde
            if user and user.check_password(password):
                return user
                
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce timing attacks
            UserModel().set_password(password)
            
        return None