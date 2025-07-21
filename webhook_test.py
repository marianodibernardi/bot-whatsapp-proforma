from flask import Flask, request
import os

app = Flask(__name__)

VERIFY_TOKEN = "123abc"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print("✅ Verificación exitosa con Meta")
            return challenge, 200
        else:
            print("❌ Error de verificación")
            return "Error de verificación", 403

    elif request.method == 'POST':
        data = request.json
        print("📩 Evento recibido:", data)
        return 'EVENT_RECEIVED', 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)