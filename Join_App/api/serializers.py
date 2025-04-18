from rest_framework import serializers
from Join_App.models import Task, Contact, Subtask
from django.contrib.auth.models import User

import logging
logger = logging.getLogger(__name__)

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'name', 'email', 'phone', 'color', 'user']
        read_only_fields = ['id']
        extra_kwargs = {'user': {'required': False}}
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['contactID'] = data.pop('id')
        data['initials'] = instance.get_initials()
        
        # Remove the user field from the response
        if 'user' in data:
            data.pop('user')
            
        return data
    
    def create(self, validated_data):
        # Get the authenticated user from the request context
        user = self.context['request'].user if 'request' in self.context else None
        
        # Ensure user is authenticated
        if not user or not user.is_authenticated:
            raise serializers.ValidationError({"user": "User must be authenticated to create contacts"})
        
        # Set the user without requiring it in the request data
        validated_data['user'] = user
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        user = self.context['request'].user if 'request' in self.context else None
        if instance.user != user:
            raise serializers.ValidationError({"error": "You can only update your own contacts"})
        if 'user' in validated_data:
            validated_data.pop('user')
            
        return super().update(instance, validated_data)

class SubtaskSerializer(serializers.ModelSerializer):
    subTaskID = serializers.IntegerField(source='id', read_only=True)
    subTaskName = serializers.CharField(source='name')
    
    class Meta:
        model = Subtask
        fields = ['subTaskID', 'subTaskName', 'done']

class ContactReferenceSerializer(serializers.Serializer):
    contactID = serializers.IntegerField()

class TaskSerializer(serializers.ModelSerializer):
    taskID = serializers.IntegerField(source='id', read_only=True)
    assignedTo = ContactReferenceSerializer(many=True, required=False)
    subtasks = SubtaskSerializer(many=True, required=False)
    dueDate = serializers.DateField(source='due_date', required=False)
    currentProgress = serializers.IntegerField(source='current_progress', required=False)
    
    class Meta:
        model = Task
        fields = ['taskID', 'title', 'description', 'assignedTo', 'dueDate', 
                'priority', 'category', 'subtasks', 'currentProgress']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Stell sicher, dass assignedTo-Daten vorhanden sind
        if not 'assignedTo' in data or not data['assignedTo']:
            data['assignedTo'] = [
                {'contactID': contact.id} 
                for contact in instance.assigned_to.all()
            ]
        return data

    def create(self, validated_data):
        assigned_to_data = validated_data.pop('assignedTo', [])
        subtasks_data = validated_data.pop('subtasks', [])
        user = self.context['request'].user if 'request' in self.context else None
        task = Task.objects.create(user=user, **validated_data)
        missing_contacts = []
        for contact_data in assigned_to_data:
            contact_id = contact_data.get('contactID')
            try:
                contact = Contact.objects.get(id=contact_id, user=user)
                task.assigned_to.add(contact)
            except Contact.DoesNotExist:
                logger.warning(
                f"Kontakt mit ID {contact_id} konnte nicht zugewiesen werden - "
                f"existiert nicht oder gehört nicht dem Benutzer {user.username}"
            )
            missing_contacts.append(contact_id)
        
        for subtask_data in subtasks_data:
            subtask_name = subtask_data.get('name')
            subtask_done = subtask_data.get('done', False)
            if subtask_name:
                Subtask.objects.create(task=task, name=subtask_name, done=subtask_done)
        
        return task
    
    def update(self, instance, validated_data):
        # Basic field updates
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.due_date = validated_data.get('due_date', instance.due_date)
        instance.priority = validated_data.get('priority', instance.priority)
        instance.category = validated_data.get('category', instance.category)
        instance.current_progress = validated_data.get('current_progress', instance.current_progress)
        instance.save()
        
        # Update assigned contacts if provided
        if 'assignedTo' in validated_data:
            assigned_to_data = validated_data.get('assignedTo', [])
            instance.assigned_to.clear()
            user = self.context['request'].user
            missing_contacts = []
            for contact_data in assigned_to_data:
                contact_id = contact_data.get('contactID')
                if contact_id:
                    try:
                        contact = Contact.objects.get(id=contact_id, user=user)
                        instance.assigned_to.add(contact)
                    except Contact.DoesNotExist:
                        logger.warning(
                        f"Kontakt mit ID {contact_id} konnte nicht zugewiesen werden - "
                        f"existiert nicht oder gehört nicht dem Benutzer {user.username}"
                    )
                    missing_contacts.append(contact_id)
        
        if 'subtasks' in validated_data:
            subtasks_data = validated_data.get('subtasks', [])
            instance.subtasks.all().delete()
            for subtask_data in subtasks_data:
                subtask_name = subtask_data.get('name')
                subtask_done = subtask_data.get('done', False)
                if subtask_name:
                    Subtask.objects.create(
                        task=instance, 
                        name=subtask_name, 
                        done=subtask_done
                    )
        
        return instance
        
class UserSerializer(serializers.ModelSerializer):
    userID = serializers.IntegerField(source='id', read_only=True)
    name = serializers.CharField(source='username')
    
    class Meta:
        model = User
        fields = ['userID', 'name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['name'],
            email=validated_data.get('email', ''),
            password=validated_data.get('password', '')
        )
        return user