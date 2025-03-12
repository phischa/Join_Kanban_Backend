from rest_framework import serializers
from Join_App.models import User, Task, Contact, Subtask

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'name', 'email', 'phone', 'color']
        read_only_fields = ['id']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['contactID'] = data.pop('id')
        data['initials'] = instance.get_initials()
        return data

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

    def create(self, validated_data):
        assigned_to_data = validated_data.pop('assignedTo', [])
        subtasks_data = validated_data.pop('subtasks', [])
        
        # Get default user
        default_user = User.objects.first()
        task = Task.objects.create(user=default_user, **validated_data)
        
        # Add contacts
        for contact_data in assigned_to_data:
            contact_id = contact_data.get('contactID')
            try:
                contact = Contact.objects.get(id=contact_id)
                task.assigned_to.add(contact)
            except Contact.DoesNotExist:
                pass
        
        # Add subtasks
        for subtask_data in subtasks_data:
            subtask_name = subtask_data.get('name')
            subtask_done = subtask_data.get('done', False)
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
        if 'assignedTo' in self.initial_data:
            instance.assigned_to.clear()
            for contact_data in self.initial_data.get('assignedTo', []):
                contact_id = contact_data.get('contactID')
                if contact_id:
                    try:
                        contact = Contact.objects.get(id=contact_id)
                        instance.assigned_to.add(contact)
                    except Contact.DoesNotExist:
                        pass
        
        # Update subtasks if provided
        if 'subtasks' in self.initial_data:
            # Remove existing subtasks 
            instance.subtasks.all().delete()
            
            # Add new subtasks
            for subtask_data in self.initial_data.get('subtasks', []):
                subtask_name = subtask_data.get('subTaskName')
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
