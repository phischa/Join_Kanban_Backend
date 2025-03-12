from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from Join_App.models import User, Task, Contact, Subtask
from .serializers import ContactSerializer, TaskSerializer, UserSerializer

@api_view(['GET'])
def first_view(request):
    return Response({"message": "Hello World!"})

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    
    def list(self, request):
        contacts = self.get_queryset()
        serializer = self.get_serializer(contacts, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        data = request.data
        
        # Handle both single contact and list of contacts
        many = isinstance(data, list)
        serializer = self.get_serializer(data=data, many=many)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        try:
            data = request.data
            contact_id = data.get('contactID')
            
            if not contact_id:
                return Response({"status": "error", "message": "No contactID provided"}, 
                                status=status.HTTP_400_BAD_REQUEST)
            
            contact = Contact.objects.get(id=contact_id)
            contact.delete()
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        except Contact.DoesNotExist:
            return Response({"status": "error", "message": "Contact not found"}, 
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, 
                            status=status.HTTP_400_BAD_REQUEST)

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    
    def list(self, request):
        tasks = self.get_queryset()
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        data = request.data
        
        # Handle both single task and list of tasks
        many = isinstance(data, list)
        serializer = self.get_serializer(data=data, many=many)
        
        if serializer.is_valid():
            serializer.save()
            
            # For single task
            if not many:
                if hasattr(serializer.instance, 'id'):
                    return Response({"status": "success", "taskID": serializer.instance.id}, 
                                status=status.HTTP_201_CREATED)
            # For multiple tasks
            else:
                return Response({"status": "success"}, status=status.HTTP_201_CREATED)
                
            return Response({"status": "success"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            task_id = data.get('taskID')
            
            if not task_id:
                return Response({"status": "error", "message": "No taskID provided"}, 
                                status=status.HTTP_400_BAD_REQUEST)
            
            task = Task.objects.get(id=task_id)
            serializer = self.get_serializer(task, data=data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response({"status": "success"}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Task.DoesNotExist:
            return Response({"status": "error", "message": "Task not found"}, 
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, 
                            status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        try:
            data = request.data
            task_id = data.get('taskID')
            
            if not task_id:
                return Response({"status": "error", "message": "No taskID provided"}, 
                                status=status.HTTP_400_BAD_REQUEST)
            
            task = Task.objects.get(id=task_id)
            task.delete()
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response({"status": "error", "message": "Task not found"}, 
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, 
                            status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def list(self, request):
        users = self.get_queryset()
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        data = request.data
        
        # Handle both single user and list of users
        many = isinstance(data, list)
        serializer = self.get_serializer(data=data, many=many)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
