from django.urls import path
from .views import home, cases, users, user, wallets, wallet, transactions, transaction, topup_requests, topup_request, case_openings, case_opening

urlpatterns = [
    path('', home, name='home'),
    
    path('cases/', cases, name='cases'),
    
    path('users/', users, name='users'),
    path('users/<str:id>/edit/', user, name='user'),

    path('wallets/', wallets, name='wallets'),
    path('wallets/<str:id>/edit/', wallet, name='wallet'),

    path('transactions/', transactions, name='transactions'),
    path('transactions/<str:id>/edit/', transaction, name='transaction'),

    path('topup_requests/', topup_requests, name='topup_requests'),
    path('topup_requests/<str:id>/edit/', topup_request,  name='topup_request'),

    path('case_openings/', case_openings, name='case_openings'),
    path('case_openings/<str:id>/edit/', case_opening,  name='case_opening'),
]
