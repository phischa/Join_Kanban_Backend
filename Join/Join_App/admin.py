from django.contrib import admin
from .models import User, Task, Contact

# Register your models here.

admin.site.register(User)
admin.site.register(Task)
admin.site.register(Contact)