from rest_framework import serializers
from Join_App.models import Task, Contact, Subtask
from django.contrib.auth.models import User

import logging
logger = logging.getLogger(__name__)

class ContactSerializer(serializers.ModelSerializer):
    """
    Serializer for the Contact model.
    
    Processes contact data for API requests and responses.
    Converts the ID to 'contactID' and adds initials.
    Ensures that only authenticated users can create contacts
    and users can only update their own contacts.
    """
    class Meta:
        model = Contact
        fields = ['id', 'name', 'email', 'phone', 'color', 'user']
        read_only_fields = ['id']
        extra_kwargs = {'user': {'required': False}}
    
    def to_representation(self, instance):
        """
        Modifies the output representation of the contact.
        
        Converts 'id' to 'contactID', adds initials, and
        removes the 'user' field from the response.
        
        Args:
            instance: Contact object being serialized
            
        Returns:
            dict: Modified representation of the contact
        """
        data = super().to_representation(instance)
        data['contactID'] = data.pop('id')
        data['initials'] = instance.get_initials()
        
        # Remove the user field from the response
        if 'user' in data:
            data.pop('user')
            
        return data
    
    def create(self, validated_data):
        """
        Creates a new contact.
        
        Extracts the authenticated user from the request context
        and sets them as the owner of the contact.
        
        Args:
            validated_data: Dict with validated data for creating the contact
            
        Returns:
            Contact: Newly created Contact object
            
        Raises:
            ValidationError: If no authenticated user is present
        """
        # Get the authenticated user from the request context
        user = self.context['request'].user if 'request' in self.context else None
        
        # Ensure user is authenticated
        if not user or not user.is_authenticated:
            raise serializers.ValidationError({"user": "User must be authenticated to create contacts"})
        
        # Set the user without requiring it in the request data
        validated_data['user'] = user
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """
        Updates an existing contact.
        
        Checks if the current user is the owner of the contact
        and removes the 'user' field from the data to be updated.
        
        Args:
            instance: Contact object to update
            validated_data: Dict with validated data for updating
            
        Returns:
            Contact: Updated Contact object
            
        Raises:
            ValidationError: If the user is not the owner of the contact
        """
        user = self.context['request'].user if 'request' in self.context else None
        if instance.user != user:
            raise serializers.ValidationError({"error": "You can only update your own contacts"})
        if 'user' in validated_data:
            validated_data.pop('user')
            
        return super().update(instance, validated_data)

class SubtaskSerializer(serializers.ModelSerializer):
    """
    Serializer for the Subtask model.
    
    Converts field names according to API conventions: 'id' to 'subTaskID' and 'name' to 'subTaskName'.
    """
    subTaskID = serializers.IntegerField(source='id', read_only=True)
    subTaskName = serializers.CharField(source='name')
    
    class Meta:
        model = Subtask
        fields = ['subTaskID', 'subTaskName', 'done']

class ContactReferenceSerializer(serializers.Serializer):
    """
    Simple serializer for referencing contacts by their ID.
    
    Used for assigning contacts to tasks.
    """
    contactID = serializers.IntegerField()

class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for the Task model.
    
    Processes complete task data including assigned contacts and subtasks.
    Converts field names according to API conventions: 'id' to 'taskID', 'due_date' to 'dueDate',
    and 'current_progress' to 'currentProgress'.
    """
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
        """
        Modifies the output representation of the task.
        
        Ensures that assigned contacts are properly represented,
        even if they are not explicitly present in the original data.
        
        Args:
            instance: Task object being serialized
            
        Returns:
            dict: Modified representation of the task
        """
        data = super().to_representation(instance)
        # Ensure that assignedTo data is present
        if not 'assignedTo' in data or not data['assignedTo']:
            data['assignedTo'] = [
                {'contactID': contact.id} 
                for contact in instance.assigned_to.all()
            ]
        return data

    def create(self, validated_data):
        """
        Creates a new task with assigned contacts and subtasks.
        
        Extracts data for contacts and subtasks from the validated data,
        creates the task, and then adds contacts and subtasks.
        
        Args:
            validated_data: Dict with validated data for creating the task
            
        Returns:
            Task: Newly created Task object with assigned contacts and subtasks
        """
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
                f"Contact with ID {contact_id} could not be assigned - "
                f"does not exist or does not belong to user {user.username}"
            )
            missing_contacts.append(contact_id)
        
        for subtask_data in subtasks_data:
            subtask_name = subtask_data.get('name')
            subtask_done = subtask_data.get('done', False)
            if subtask_name:
                Subtask.objects.create(task=task, name=subtask_name, done=subtask_done)
        
        return task
    
    def update(self, instance, validated_data):
        """
        Updates an existing task with assigned contacts and subtasks.
        
        Updates basic fields of the task and then processes
        updated contact assignments and subtasks, if provided.
        
        Args:
            instance: Task object to update
            validated_data: Dict with validated data for updating
            
        Returns:
            Task: Updated Task object with updated contacts and subtasks
        """
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
                        f"Contact with ID {contact_id} could not be assigned - "
                        f"does not exist or does not belong to user {user.username}"
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
    """
    Serializer for Django's User model.
    
    Converts field names according to API conventions: 'id' to 'userID' and 'username' to 'name'.
    Ensures that the password is only used for writing and is securely stored.
    """
    userID = serializers.IntegerField(source='id', read_only=True)
    name = serializers.CharField(source='username')
    
    class Meta:
        model = User
        fields = ['userID', 'name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        """
        Creates a new user.
        
        Uses Django's create_user method to ensure secure password hashing.
        
        Args:
            validated_data: Dict with validated data for creating the user
            
        Returns:
            User: Newly created User object with securely stored password
        """
        user = User.objects.create_user(
            username=validated_data['name'],
            email=validated_data.get('email', ''),
            password=validated_data.get('password', '')
        )
        return user