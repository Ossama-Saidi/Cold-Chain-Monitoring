from django.db import models
from django.contrib.auth.models import User

class Capteur(models.Model):
    nom = models.CharField(max_length=100)
    localisation = models.CharField(max_length=100)
    seuil_min = models.FloatField(default=2)
    seuil_max = models.FloatField(default=8)

    def __str__(self):
        return self.nom


class Mesure(models.Model):
    capteur = models.ForeignKey(Capteur, on_delete=models.CASCADE)
    temperature = models.FloatField()
    humidite = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)


class Ticket(models.Model):
    STATUTS = [
        ('ouvert', 'Ouvert'),
        ('assigné', 'Assigné'),
        ('en_cours', 'En cours'),
        ('clos', 'Clos'),
    ]

    capteur = models.ForeignKey(Capteur, on_delete=models.CASCADE)
    statut = models.CharField(max_length=20, choices=STATUTS, default='ouvert')
    priorite = models.CharField(max_length=10, default='haute')
    assigne_a = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    titre = models.CharField(max_length=100, default="Alerte")
    description = models.TextField(blank=True, null=True)

class AuditLog(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=200)
    objet = models.CharField(max_length=200, default="Inconnu")
    details = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

