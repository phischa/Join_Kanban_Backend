from rest_framework import serializers
from user_auth_app.models import UserProfile
from django.contrib.auth.models import User

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user', 'id']

class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True}
        }
    
    def save(self):
        pw = self.validated_data['password']
        repeated_pw = self.validated_data['repeated_password']
        email = self.validated_data['email']
        username = self.validated_data['username']

        if pw != repeated_pw:
            raise serializers.ValidationError({'password': 'Passwords do not match'})
        
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'Email already exists'})
            
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({'username': 'Username already exists'})
        
        account = User(email=email, username=username)
        account.set_password(pw)
        account.save()
        
        # Create UserProfile for the new user
        UserProfile.objects.create(user=account)
        
        return account