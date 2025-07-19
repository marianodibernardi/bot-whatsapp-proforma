from flask import Flask
from routes.webhook import webhook_bp

app = Flask(__name__)
app.register_blueprint(webhook_bp)
