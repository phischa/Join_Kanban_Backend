from django.contrib import admin
from django.urls import path, include
from Join_App.api import urls as join_app_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(join_app_urls)),
    path('user_auth/', include('user_auth_app.api.urls')),
]