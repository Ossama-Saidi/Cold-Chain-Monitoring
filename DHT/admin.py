# Register your models here.
from django.contrib import admin
from .models import Capteur, Mesure, Ticket, AuditLog

admin.site.register(Capteur)
admin.site.register(Mesure)
admin.site.register(Ticket)
admin.site.register(AuditLog)
