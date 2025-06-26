from django.urls import path
from .views import home, cases, users, user, wallets, wallet

urlpatterns = [
    path('', home, name='home'),
    
    path('cases/', cases, name='cases'),
    
    path('users/', users, name='users'),
    path('users/<str:id>/edit/', user, name='user'),

    path('wallets/', wallets, name='wallets'),
    path('wallets/<str:id>/edit/', wallet, name='wallet'),
]
