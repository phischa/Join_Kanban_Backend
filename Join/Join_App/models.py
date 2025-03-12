from django.db import models
#from phonenumber_field.modelfields import PhoneNumberField

from django.db import models

class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255, null=True, blank=True)  # In production, use proper authentication
    
    def __str__(self):
        return self.username

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    color = models.CharField(max_length=7, default="#6e6ee5")  # Hex color code
    
    def __str__(self):
        return f"{self.name}, {self.email}"
    
    def get_initials(self):
        parts = self.name.split()
        if len(parts) > 1:
            return parts[0][0].upper() + parts[-1][0].upper()
        return parts[0][0].upper() if parts else ""

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    CATEGORY_CHOICES = [
        ('todo', 'To Do'),
        ('inprogress', 'In Progress'),
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
        return self.title

class Subtask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    name = models.CharField(max_length=100)
    done = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name