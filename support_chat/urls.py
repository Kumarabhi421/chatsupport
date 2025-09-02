
# project/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Frontend Chat Page
    path('', include('chat.urls')),  

    # All API Endpoints will be under `/api/`
    path('api/', include('chat.urls')), 
     
]

