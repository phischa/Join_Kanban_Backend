from django.db import models
from django.contrib.auth.models import User 
from django.contrib.auth import get_user_model

class Contact(models.Model):
    """
    Model representing a contact that can be assigned to tasks.
    
    Each contact belongs to a specific user and contains basic contact information
    such as name, email, phone, and a color for UI representation.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')  # Added user field
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    color = models.CharField(max_length=7, default="#6e6ee5")  # Hex color code
    
    def __str__(self):
        """
        String representation of the Contact.
        
        Returns:
            str: Name and email of the contact.
        """
        return f"{self.name}, {self.email}"
    
    def get_initials(self):
        """
        Generates initials from the contact's name.
        
        Takes the first letter of the first name and the first letter of the last name.
        If only one name is provided, returns just the first letter of that name.
        
        Returns:
            str: Uppercase initials based on the contact's name.
        """
        parts = self.name.split()
        if len(parts) > 1:
            return parts[0][0].upper() + parts[-1][0].upper()
        return parts[0][0].upper() if parts else ""

class Task(models.Model):
    """
    Model representing a task in the task management system.
    
    Tasks have various attributes including title, description, assigned contacts,
    due date, priority level, category/status, and progress tracking.
    Each task belongs to a specific user and can have multiple subtasks.
    """
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('urgent', 'Urgent'),
    ]
    
    CATEGORY_CHOICES = [
        ('todo', 'To Do'),
        ('inprogress', 'In Progress'),
        ('awaitfeedback','Await Feedback'),
        ('done', 'Done'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    assigned_to = models.ManyToManyField(Contact, related_name='assigned_tasks', blank=True)
    due_date = models.DateField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES, default='todo')
    current_progress = models.IntegerField(default=0)
    
    def __str__(self):
        """
        String representation of the Task.
        
        Returns:
            str: Title of the task.
        """
        return self.title

class Subtask(models.Model):
    """
    Model representing a subtask within a main task.
    
    Subtasks provide a way to break down complex tasks into smaller,
    manageable components that can be checked off individually.
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    name = models.CharField(max_length=100)
    done = models.BooleanField(default=False)
    
    def __str__(self):
        """
        String representation of the Subtask.
        
        Returns:
            str: Name of the subtask.
        """
        return self.name