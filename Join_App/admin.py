from django.contrib import admin
from .models import Task, Subtask, Contact

# Register your models here.

admin.site.register(Contact)
admin.site.register(Task)
admin.site.register(Subtask)