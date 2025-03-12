from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from .models import User, Task, Contact
from django.views.decorators.csrf import csrf_exempt
import json

@api_view(['GET'])
def first_view(request):
    return Response({"message":"Hello World!"})

@api_view(['GET', 'POST'])
@csrf_exempt
def contacts_view(request):
    if request.method == 'GET':
        contacts = Contact.objects.all()
        contacts_list = []
        for contact in contacts:
            contacts_list.append({
                'contactID': contact.id,
                'name': contact.name,
                'email': contact.email,
                'initials': contact.name.split(' ')[0][0] + contact.name.split(' ')[-1][0] if ' ' in contact.name else contact.name[0],
                'color': '#' + ''.join([hex(ord(c) % 16)[2:] for c in contact.name[:3]]),  # Simple color generation
            })
        return JsonResponse(contacts_list, safe=False)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Check if it's a single contact or a list
            if isinstance(data, list):
                for contact_data in data:
                    Contact.objects.create(
                        name=contact_data.get('name', ''),
                        email=contact_data.get('email', '')
                    )
            else:
                Contact.objects.create(
                    name=data.get('name', ''),
                    email=data.get('email', '')
                )
            
            return JsonResponse({"status": "success"}, status=201)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

@api_view(['GET', 'POST'])
@csrf_exempt
def tasks_view(request):
    if request.method == 'GET':
        tasks = Task.objects.all()
        tasks_list = []
        for task in tasks:
            tasks_list.append({
                'taskID': task.id,
                'title': task.title,
                'description': task.description,
                'dueDate': task.date,
                'priority': 'high' if task.prio else 'normal',
                'currentProgress': 0,  # Default value, adjust as needed
            })
        return JsonResponse(tasks_list, safe=False)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Assuming there's at least one user in the database
            default_user = User.objects.first()
            
            # Handle both single task and task list
            if isinstance(data, list):
                for task_data in data:
                    Task.objects.create(
                        user=default_user,
                        title=task_data.get('title', ''),
                        description=task_data.get('description', ''),
                        date=task_data.get('dueDate', '2023-01-01'),
                        prio=(task_data.get('priority', 'normal') == 'high')
                    )
            else:
                Task.objects.create(
                    user=default_user,
                    title=data.get('title', ''),
                    description=data.get('description', ''),
                    date=data.get('dueDate', '2023-01-01'),
                    prio=(data.get('priority', 'normal') == 'high')
                )
            
            return JsonResponse({"status": "success"}, status=201)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

@api_view(['GET', 'POST'])
@csrf_exempt
def users_view(request):
    if request.method == 'GET':
        users = User.objects.all()
        users_list = []
        for user in users:
            users_list.append({
                'userID': user.id,
                'name': user.username,
                'email': user.email,
            })
        return JsonResponse(users_list, safe=False)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Handle both single user and user list
            if isinstance(data, list):
                for user_data in data:
                    User.objects.create(
                        username=user_data.get('name', ''),
                        email=user_data.get('email', '')
                    )
            else:
                User.objects.create(
                    username=data.get('name', ''),
                    email=data.get('email', '')
                )
            
            return JsonResponse({"status": "success"}, status=201)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
