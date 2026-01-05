import logging
import requests
from django.conf import settings
from django.core.mail import send_mail
from twilio.rest import Client
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone

logger = logging.getLogger(__name__)

def format_alert_message(capteur_name, temperature, humidite):
    now = timezone.now().strftime("%d/%m/%Y %H:%M:%S")
    projet_name = "Cold Chain Monitoring"

    message = (
        f"⚠ Alerte {projet_name} ⚠\n\n"
        f"Capteur : {capteur_name}\n"
        f"Température : {temperature} °C\n"
        f"Humidité : {humidite} %\n"
        f"Seuil recommandé : {getattr(settings, 'TEMP_THRESHOLD', 25)} °C\n"
        f"Date / Heure : {now}\n\n"
        f"Merci de prendre les mesures nécessaires.\n"
        f"Ce message a été généré automatiquement par {projet_name}."
    )
    return message

# ===============================
# 📧 Email
# ===============================

def send_email_alert(subject, capteur_name, temperature, humidite):
    recipients = getattr(settings, "ALERT_EMAIL_RECIPIENTS", [])
    if not recipients:
        return

    now = timezone.now().strftime("%d/%m/%Y %H:%M:%S")
    projet_name = "Cold Chain Monitoring"  # Nom du projet / entreprise

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <h2 style="color: #d9534f;">⚠ Alerte {projet_name}</h2>
        <p>Bonjour,</p>
        <p>Une mesure critique a été détectée pour le <strong>capteur {capteur_name}</strong> :</p>
        <ul>
            <li><strong>Température :</strong> {temperature} °C</li>
            <li><strong>Humidité :</strong> {humidite} %</li>
            <li><strong>Date / Heure :</strong> {now}</li>
        </ul>
        <p>Seuils acceptables : {getattr(settings, "TEMP_THRESHOLD", 25)} °C</p>
        <p>Merci de prendre les mesures nécessaires pour corriger cette situation.</p>
        <br>
        <p style="font-size: 0.9em; color: #555;">
            Ce message a été généré automatiquement par le système <strong>{projet_name}</strong>.
        </p>
    </body>
    </html>
    """

    try:
        msg = EmailMultiAlternatives(
            subject=f"[{projet_name}] {subject}",
            body=f"Alerte pour le capteur {capteur_name}. Température: {temperature}°C, Humidité: {humidite}%",
            from_email=settings.EMAIL_HOST_USER,
            to=recipients
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erreur envoi email: {e}")

# ===============================
# 🤖 Telegram
# ===============================
def send_telegram_alert(capteur_name, temperature, humidite):
    import requests
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", None)
    chat_id = getattr(settings, "TELEGRAM_CHAT_ID", None)
    if not token or not chat_id:
        return

    message = format_alert_message(capteur_name, temperature, humidite)

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        r = requests.post(url, data=payload)
        if r.status_code == 200:
            print("Alerte Telegram envoyée")
        else:
            print(f"Erreur Telegram: {r.text}")
    except Exception as e:
        print(f"Exception Telegram: {e}")

# ===============================
# 💬 WhatsApp via Twilio
# ===============================
def send_whatsapp_alert(capteur_name, temperature, humidite):
    from twilio.rest import Client
    account_sid = getattr(settings, "TWILIO_ACCOUNT_SID", None)
    auth_token = getattr(settings, "TWILIO_AUTH_TOKEN", None)
    twilio_number = getattr(settings, "TWILIO_PHONE_NUMBER", None)
    alert_number = getattr(settings, "ALERT_PHONE_NUMBER", None)
    if not all([account_sid, auth_token, twilio_number, alert_number]):
        return

    message = format_alert_message(capteur_name, temperature, humidite)

    try:
        client = Client(account_sid, auth_token)
        msg = client.messages.create(
            from_='whatsapp:' + twilio_number,
            body=message,
            to='whatsapp:' + alert_number
        )
        print(f"WhatsApp envoyé, SID: {msg.sid}")
    except Exception as e:
        print(f"Erreur WhatsApp: {e}")

# ===============================
# 📞 Appel vocal Twilio
# ===============================
def send_voice_call(capteur_name, temperature, humidite):
    from twilio.rest import Client
    account_sid = getattr(settings, "TWILIO_ACCOUNT_SID", None)
    auth_token = getattr(settings, "TWILIO_AUTH_TOKEN", None)
    twilio_number = getattr(settings, "TWILIO_PHONE_NUMBER", None)
    alert_number = getattr(settings, "ALERT_PHONE_NUMBER", None)
    if not all([account_sid, auth_token, twilio_number, alert_number]):
        return

    message = format_alert_message(capteur_name, temperature, humidite)
    
    # Pour l'appel vocal, simplifier le message pour être lu clairement
    voice_message = (
        f"Alerte {capteur_name}. "
        f"Température {temperature} degrés. "
        f"Humidité {humidite} pour cent. "
        "Merci de prendre les mesures nécessaires."
    )

    try:
        client = Client(account_sid, auth_token)
        call = client.calls.create(
            to=alert_number,
            from_=twilio_number,
            twiml=f'<Response><Say>{voice_message}</Say></Response>'
        )
        print(f"Appel vocal lancé, SID: {call.sid}")
    except Exception as e:
        print(f"Erreur appel vocal: {e}")

