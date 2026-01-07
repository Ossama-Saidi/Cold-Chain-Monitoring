from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *

urlpatterns = [
    path('', api_root),
    
    # Authentification
    path('auth/register/', register, name='register'),
    path('auth/login/', login, name='login'),
    path('auth/logout/', logout, name='logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', user_profile, name='user_profile'),
    
    # API
    path('mesures/', create_mesure),
    path('mesures/list/', list_mesures),
    path('tickets/', list_tickets),
    path('tickets/<int:pk>/', update_ticket),
    path('auditlogs/', list_auditlogs),
]
