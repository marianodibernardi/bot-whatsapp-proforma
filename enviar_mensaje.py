import os
from twilio.rest import Client

# Credenciales desde Live credentials
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

client = Client(account_sid, auth_token)

# Números para el sandbox
from_whatsapp_number = os.getenv("FROM_WHATSAPP_NUMBER")
to_whatsapp_number   = os.getenv("TO_WHATSAPP_NUMBER")


# Enviar el mensaje
message = client.messages.create(
    body='Hola, este es un mensaje de prueba desde Twilio WhatsApp API 😃',
    from_=from_whatsapp_number,
    to=to_whatsapp_number
)

