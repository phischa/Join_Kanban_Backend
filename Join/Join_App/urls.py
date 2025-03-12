from django.urls import path
from .views import first_view, contacts_view, tasks_view, users_view

urlpatterns = [
    path('', first_view),
    path('contacts/', contacts_view),
    path('tasks/', tasks_view),
    path('users/', users_view),
]