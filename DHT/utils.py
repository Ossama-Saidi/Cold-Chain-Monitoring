# import requests
# from django.core.mail import send_mail
# from django.conf import settings


# def send_telegram(text: str) -> bool:
#     """Envoie un message Telegram via l’API officielle."""
#     token = settings.TELEGRAM_BOT_TOKEN
#     chat_id = settings.TELEGRAM_CHAT_ID
#     url = f"https://api.telegram.org/bot{token}/sendMessage"
#     try:
#         r = requests.post(url, data={"chat_id": chat_id, "text": text})
#         return r.ok
#     except Exception:
#         return False


# def send_email_alert(subject: str, message: str, recipient: str) -> bool:
#     """Envoie un email d’alerte via la configuration SMTP Django."""
#     try:
#         send_mail(
#             subject=subject,
#             message=message,
#             from_email=settings.EMAIL_HOST_USER,
#             recipient_list=[recipient],
#             fail_silently=False,  # mets True si tu veux ignorer les erreurs
#         )
#         return True
#     except Exception as e:
#         print("Erreur d’envoi email :", e)
#         return False
