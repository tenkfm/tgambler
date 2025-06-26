from django.urls import path
from .views import home, cases, users, user

urlpatterns = [
    path('', home, name='home'),
    
    path('cases/', cases, name='cases'),
    
    path('users/', users, name='users'),
    path('users/<str:id>/edit/', user, name='user'),
]
