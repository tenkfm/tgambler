# case_manager/case_manager/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),  # ← подключаем app/urls.py по абсолютному пути
]
