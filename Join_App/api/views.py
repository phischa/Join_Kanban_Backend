from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.http import JsonResponse
from django.contrib.auth.models import User
from Join_App.models import Task, Contact, Subtask
from .serializers import ContactSerializer, TaskSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated


#UserSerializer
#BoardSerializer

#class BoardViewSet(viewsets,ModelViewset):
#    queryset = Board.objects.all()
#    serializer_class = BoardSerializer
#    permission_classes = [isOwner]

class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]
    queryset = Contact.objects.all()

    def get_queryset(self):
        # Filter contacts by authenticated user
        if self.request.user.is_authenticated:
            return Contact.objects.filter(user=self.request.user)
        return Contact.objects.none()
    
    def get_serializer_context(self):
        # Pass request to serializer for user access
        context = super().get_serializer_context()
        return context

    def get_serializer(self, *args, **kwargs):
        """
        Handle both single item and list serialization.
        """
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)

    def list(self, request):
        contacts = self.get_queryset()
        serializer = self.get_serializer(contacts, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
    
        if serializer.is_valid():
            contact = serializer.save(user=request.user)
            return Response({
                "status": "success", 
                "contactID": contact.id,
                "message": "Contact created successfully"
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]  # Require authentication
    
    def get_queryset(self):
        # Filter tasks by authenticated user
        if self.request.user.is_authenticated:
            return Task.objects.filter(user=self.request.user)
        return Task.objects.none()
    
    def get_serializer_context(self):
        # Pass request to serializer for user access
        context = super().get_serializer_context()
        return context
    
    def get_serializer(self, *args, **kwargs):
        """
        Handle both single item and list serialization.
        """
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)
    
    def list(self, request):
        tasks = self.get_queryset()
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            instance = serializer.save()
            
            if not isinstance(request.data, list) and hasattr(instance, 'id'):
                return Response(
                    {"status": "success", "taskID": instance.id}, 
                    status=status.HTTP_201_CREATED
                )
            return Response({"status": "success"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    
    def get_queryset(self):
        # If admin, show all users. Otherwise, only show the current user
        user = self.request.user
        if user.is_authenticated:
            if user.is_staff:
                return User.objects.all()
            return User.objects.filter(id=user.id)
        return User.objects.none()
    
    def get_serializer(self, *args, **kwargs):
        """
        Handle both single item and list serialization.
        """
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)
    
    def list(self, request):
        users = self.get_queryset()
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        # Note: This should normally be handled by the registration view
        # But keeping it for completeness/admin functionality
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def hello_world(request):
    return Response({"message": "Hello World!"})