from django.contrib import admin
from django.urls import path, include
from Join_App.api import urls as join_app_urls 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(join_app_urls)),
]
