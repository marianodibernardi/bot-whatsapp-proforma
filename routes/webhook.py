from flask import Blueprint, request
from handle_text_message import handle_text_message
from handlers.media_handler import handle_media_message

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    data = request.form
    if "MediaContentType0" in data:
        return handle_media_message(data)
    else:
        return handle_text_message(data)
