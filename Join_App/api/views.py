from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.http import JsonResponse
from django.contrib.auth.models import User
from Join_App.models import Task, Contact, Subtask
from .serializers import ContactSerializer, TaskSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated

class ContactViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Contact objects.
    
    Provides CRUD operations for contacts with proper authentication.
    Only returns contacts owned by the authenticated user.
    """
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]
    queryset = Contact.objects.all()

    def get_queryset(self):
        """
        Returns contacts filtered by the authenticated user.
        
        Returns:
            QuerySet: Contact objects belonging to the authenticated user,
            or an empty QuerySet if not authenticated.
        """ 
        if self.request.user.is_authenticated:
            return Contact.objects.filter(user=self.request.user)
        return Contact.objects.none()
    
    def get_serializer_context(self):
        """
        Passes request context to serializer.
        
        Returns:
            dict: Context containing the request.
        """
        context = super().get_serializer_context()
        return context

    def get_serializer(self, *args, **kwargs):
        """
        Handle both single item and list serialization.
        
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
            
        Returns:
            Serializer: The appropriate serializer instance.
        """
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)

    def list(self, request):
        """
        Lists all contacts belonging to the authenticated user.
        
        Args:
            request: The HTTP request.
            
        Returns:
            Response: Serialized contacts data.
        """
        contacts = self.get_queryset()
        serializer = self.get_serializer(contacts, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        """
        Creates a new contact for the authenticated user.
        
        Args:
            request: The HTTP request containing contact data.
            
        Returns:
            Response: Success message with contactID if created,
            or validation errors.
        """
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
    """
    ViewSet for managing Task objects.
    
    Provides CRUD operations for tasks with proper authentication.
    Only returns tasks owned by the authenticated user.
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Returns tasks filtered by the authenticated user.
        
        Returns:
            QuerySet: Task objects belonging to the authenticated user,
            or an empty QuerySet if not authenticated.
        """
        if self.request.user.is_authenticated:
            return Task.objects.filter(user=self.request.user)
        return Task.objects.none()
    
    def get_serializer_context(self):
        """
        Passes request context to serializer.
        
        Returns:
            dict: Context containing the request.
        """
        context = super().get_serializer_context()
        return context
    
    def get_serializer(self, *args, **kwargs):
        """
        Handle both single item and list serialization.
        
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
            
        Returns:
            Serializer: The appropriate serializer instance.
        """
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)
    
    def list(self, request):
        """
        Lists all tasks belonging to the authenticated user.
        
        Args:
            request: The HTTP request.
            
        Returns:
            Response: Serialized tasks data.
        """
        tasks = self.get_queryset()
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
def create(self, request):
    """
    Creates a new task for the authenticated user.
    
    Handles the case of missing contacts and adds warnings to the response
    if some contacts could not be assigned.
    
    Args:
        request: The HTTP request containing task data.
        
    Returns:
        Response: Success message with taskID and optional warnings if created,
        or validation errors.
    """
    serializer = self.get_serializer(data=request.data)
    
    if serializer.is_valid():
        instance = serializer.save()
        response_data = {"status": "success", "taskID": instance.id}
        if hasattr(instance, 'missing_contacts') and instance.missing_contacts:
            response_data["warnings"] = {
                "missing_contacts": instance.missing_contacts
            }
            
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing User objects.
    
    Provides CRUD operations for users.
    Regular users can only see and modify their own user,
    while staff users can access all users.
    """
    serializer_class = UserSerializer
    
    def get_queryset(self):
        """
        Returns users filtered by permissions.
        
        Staff users see all users, while regular users only see themselves.
        
        Returns:
            QuerySet: User objects based on permission,
            or an empty QuerySet if not authenticated.
        """
        user = self.request.user
        if user.is_authenticated:
            if user.is_staff:
                return User.objects.all()
            return User.objects.filter(id=user.id)
        return User.objects.none()
    
    def get_serializer(self, *args, **kwargs):
        """
        Handle both single item and list serialization.
        
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
            
        Returns:
            Serializer: The appropriate serializer instance.
        """
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)
    
    def list(self, request):
        """
        Lists users based on permissions.
        
        Args:
            request: The HTTP request.
            
        Returns:
            Response: Serialized users data.
        """
        users = self.get_queryset()
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        """
        Creates a new user.
        
        This is primarily for admin functionality.
        Regular user registration should normally use a dedicated registration view.
        
        Args:
            request: The HTTP request containing user data.
            
        Returns:
            Response: Success message if created, or validation errors.
        """
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def hello_world(request):
    """
    A simple API view that returns a hello message.
    
    Args:
        request: The HTTP request.
        
    Returns:
        Response: A JSON response with a "Hello World!" message.
    """
    return Response({"message": "Hello World!"})