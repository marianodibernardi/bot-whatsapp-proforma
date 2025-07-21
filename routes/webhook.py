from flask import Blueprint, request
import requests
import os

from handle_text_message import handle_text_message
from handlers.media_handler import handle_media_message

webhook_bp = Blueprint("webhook", __name__)
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")

# 🔐 Token y phone_number_id desde variables de entorno
ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("META_PHONE_NUMBER_ID")

def enviar_respuesta(to_number, mensaje):
    """Envía una respuesta de texto usando la API de Meta"""
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {
            "body": mensaje
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    print("📤 Respuesta enviada:", response.status_code, response.text)

@webhook_bp.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        print("🔵 GET recibido:", request.args)
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("✅ Verificación exitosa, challenge:", challenge)
            return challenge, 200
        else:
            print("❌ Verificación fallida")
            return "Verification failed", 403

    if request.method == "POST":
        data = request.get_json()
        print("📩 JSON recibido de Meta:", data)

        try:
            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    messages = value.get("messages", [])
                    for message in messages:
                        from_number = message["from"]

                        if "text" in message:
                            respuesta = handle_text_message(message)
                            enviar_respuesta(from_number, respuesta)

                        elif "image" in message:
                            respuesta = handle_media_message(message, ACCESS_TOKEN)
                            enviar_respuesta(from_number, respuesta)

                        else:
                            enviar_respuesta(from_number, "🤖 Aún no puedo procesar ese tipo de mensaje.")
        except Exception as e:
            print("⚠️ Error al procesar mensaje:", e)

        return "EVENT_RECEIVED", 200
