from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.contrib.auth.models import User
from .models import *
from .serializers import *
from .alerts import send_email_alert, send_telegram_alert, send_whatsapp_alert, send_voice_call

def log_action(user, action, objet):
    if user and user.is_authenticated:
        AuditLog.objects.create(user=user, action=action, objet=objet)
    else:
        AuditLog.objects.create(user=None, action=action, objet=objet)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Enregistrer un nouvel utilisateur"""
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        log_action(user, "Inscription", f"Utilisateur {user.username}")
        return Response({
            "message": "Utilisateur créé avec succès",
            "user": UserSerializer(user).data
        }, status=201)
    return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Authentifier un utilisateur et retourner les tokens JWT"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        log_action(user, "Connexion", f"Utilisateur {user.username}")
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })
    return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Déconnecter l'utilisateur"""
    try:
        user = request.user
        log_action(user, "Déconnexion", f"Utilisateur {user.username}")
        return Response({"message": "Déconnecté avec succès"})
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Récupérer le profil de l'utilisateur connecté"""
    return Response(UserSerializer(request.user).data)


@api_view(['GET'])
def api_root(request):
    return Response({
        "auth": {
            "register": "/api/auth/register/",
            "login": "/api/auth/login/",
            "logout": "/api/auth/logout/",
            "refresh": "/api/auth/refresh/",
            "profile": "/api/auth/profile/",
        },
        "mesures_post": "/api/mesures/",
        "mesures_list": "/api/mesures/list/",
        "tickets": "/api/tickets/",
        "ticket_update": "/api/tickets/<id>/",
        "auditlogs": "/api/auditlogs/",
    })
    
@api_view(['POST'])
def create_mesure(request):
    serializer = MesureSerializer(data=request.data)
    if serializer.is_valid():
        mesure = serializer.save()
        capteur = mesure.capteur

        # Vérifier seuils
        if mesure.temperature < capteur.seuil_min or mesure.temperature > capteur.seuil_max:
            message = f"Alerte! Capteur {capteur.nom} hors seuil: {mesure.temperature}°C"
            
            # Envoyer alertes multi-canaux
            send_email_alert("Alerte Température Critique", capteur.nom, mesure.temperature, mesure.humidite)
            send_telegram_alert(capteur.nom, mesure.temperature, mesure.humidite)
            send_whatsapp_alert(capteur.nom, mesure.temperature, mesure.humidite)
            send_voice_call(capteur.nom, mesure.temperature, mesure.humidite)
                    
            # Créer ticket automatiquement
            Ticket.objects.create(capteur=capteur, priorite='haute')
        
        log_action(None, "Nouvelle mesure", f"Capteur {capteur.nom}")
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)


@api_view(['GET'])
def list_mesures(request):
    mesures = Mesure.objects.all().order_by('-timestamp')[:200]
    return Response(MesureSerializer(mesures, many=True).data)


@api_view(['GET'])
def list_tickets(request):
    tickets = Ticket.objects.all()
    return Response(TicketSerializer(tickets, many=True).data)


@api_view(['PATCH'])
def update_ticket(request, pk):
    ticket = Ticket.objects.get(id=pk)
    serializer = TicketSerializer(ticket, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        log_action(request.user, "Update Ticket", f"Ticket {pk}")
        return Response(serializer.data)


@api_view(['GET'])
def list_auditlogs(request):
    logs = AuditLog.objects.all().order_by('-timestamp')
    serializer = AuditLogSerializer(logs, many=True)
    return Response(serializer.data)

