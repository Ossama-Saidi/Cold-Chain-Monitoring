from django.urls import path
from .views import *

urlpatterns = [
    path('', api_root),
    path('mesures/', create_mesure),
    path('mesures/list/', list_mesures),
    path('tickets/', list_tickets),
    path('tickets/<int:pk>/', update_ticket),
    path('auditlogs/', list_auditlogs),
]
