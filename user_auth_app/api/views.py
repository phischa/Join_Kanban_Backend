from rest_framework import generics, status
from user_auth_app.models import UserProfile
from .serializers import UserProfileSerializer, RegistrationSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from django.contrib.auth.models import User  # Diese Zeile wurde hinzugefügt
import logging

logger = logging.getLogger(__name__)

class UserProfileList(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                saved_account = serializer.save()
                token, created = Token.objects.get_or_create(user=saved_account)
                return Response({
                    'status': 'success',
                    'token': token.key,
                    'username': saved_account.username,
                    'email': saved_account.email,
                    'userID': saved_account.id  # ID zurückgeben für Frontend
                })
            except Exception as e:
                return Response({
                    'status': 'error',
                    'message': str(e)
                }, status=500)
        else:
            # Formatierter Fehler mit flacher Struktur für einfachere Frontend-Verarbeitung
            errors = {}
            for field, error_msgs in serializer.errors.items():
                errors[field] = error_msgs[0] if error_msgs else "Invalid data"
            
            return Response({
                'status': 'error',
                'errors': errors
            }, status=400)
    
class CustomLoginView(ObtainAuthToken):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        data = {}

        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            data = {
                'token': token.key,
                'username': user.username,
                'email': user.email
            }
        else: 
            data = serializer.errors
        return Response(data)