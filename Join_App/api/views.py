from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.http import JsonResponse
from Join_App.models import User, Task, Contact, Subtask
from .serializers import ContactSerializer, TaskSerializer, UserSerializer


class ContactViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing contacts.
    Provides CRUD operations and additional functionality.
    """
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def get_serializer(self, *args, **kwargs):
        """
        Handle both single item and list serialization.
        """
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)

    def list(self, request):
        """
        Get all contacts.
        """
        contacts = self.get_queryset()
        serializer = self.get_serializer(contacts, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        """
        Create one or multiple contacts.
        """
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tasks.
    Provides CRUD operations and additional functionality.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    
    def get_serializer(self, *args, **kwargs):
        """
        Handle both single item and list serialization.
        """
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)
    
    def list(self, request):
        """
        Get all tasks.
        """
        tasks = self.get_queryset()
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        """
        Create one or multiple tasks.
        """
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            instance = serializer.save()
            
            # For single task, return the ID
            if not isinstance(request.data, list) and hasattr(instance, 'id'):
                return Response(
                    {"status": "success", "taskID": instance.id}, 
                    status=status.HTTP_201_CREATED
                )
                
            return Response({"status": "success"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users.
    Provides CRUD operations.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_serializer(self, *args, **kwargs):
        """
        Handle both single item and list serialization.
        """
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)
    
    def list(self, request):
        """
        Get all users.
        """
        users = self.get_queryset()
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        """
        Create one or multiple users.
        """
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def hello_world(request):
    """
    Simple hello world endpoint.
    """
    return Response({"message": "Hello World!"})