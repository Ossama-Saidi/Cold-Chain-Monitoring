import os
import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Mesure, Ticket, AuditLog

TEMP_MIN = 2.0
TEMP_MAX = 8.0


@receiver(post_save, sender=Mesure)
def check_temperature(sender, instance, created, **kwargs):
    if not created:
        return

    temp = instance.temperature

    if temp < TEMP_MIN or temp > TEMP_MAX:
        # 1️⃣ Ticket
        ticket = Ticket.objects.create(
            titre="Alerte température hors seuil",
            description=f"Température détectée : {temp}°C",
            capteur=instance.capteur
        )

        # 2️⃣ Audit log
        AuditLog.objects.create(
            action="Création automatique de ticket",
            details=f"Ticket #{ticket.id} créé (Temp={temp}°C)"
        )

        # 3️⃣ Email
        try:
            send_mail(
                subject="🚨 Alerte chaîne du froid",
                message=f"Température anormale : {temp}°C",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=settings.ALERT_EMAILS,
                fail_silently=True
            )
        except Exception as e:
            AuditLog.objects.create(
                action="Erreur email",
                details=str(e)
            )

        # 4️⃣ Telegram
        try:
            token = os.environ.get("TELEGRAM_BOT_TOKEN")
            chat_id = os.environ.get("TELEGRAM_CHAT_ID")
            if token and chat_id:
                requests.post(
                    f"https://api.telegram.org/bot{token}/sendMessage",
                    data={"chat_id": chat_id, "text": f"🚨 Température anormale : {temp}°C"}
                )
        except Exception as e:
            AuditLog.objects.create(
                action="Erreur Telegram",
                details=str(e)
            )
