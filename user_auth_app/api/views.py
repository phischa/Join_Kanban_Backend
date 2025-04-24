from rest_framework import generics, status
from user_auth_app.models import UserProfile
from .serializers import UserProfileSerializer, RegistrationSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
import uuid
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny])
def guest_test(request):
    return Response({"message": "Guest test endpoint works!"})

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

class GuestLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        guest_username = f"guest_{uuid.uuid4().hex[:8]}"
        temp_password = uuid.uuid4().hex
        guest_user = User.objects.create_user(
            username = guest_username,
            email = f"{guest_username}@example.com",
            password = temp_password
        )
        profile = guest_user.profile
        profile.is_guest = True
        profile.save()
        
        token, _ = Token.objects.get_or_create(user=guest_user)
        
        return Response({
            'status': 'success',
            'token': token.key,
            'username': guest_username,
            'email': f"{guest_username}@example.com",
            'is_guest': True
        })