#!/bin/bash

# 🔐 Authtoken real
ngrok config add-authtoken 2nQnItkVcs4M0EIeeOiSlIXtNIv_685aXSmJcqa6WKWvHPWAC

# 🌐 Iniciar ngrok en segundo plano
ngrok http 5000 --log=stdout > /tmp/ngrok.log &

# ⏳ Esperar a que el túnel esté listo (más tiempo)
echo "⏳ Esperando que ngrok genere el túnel..."
sleep 6

# 🔍 Obtener la URL pública del túnel
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o 'https://[a-zA-Z0-9.-]*.ngrok.io' | head -n 1)

# 🖨️ Mostrar el resultado
if [ -z "$NGROK_URL" ]; then
  echo "❌ No se pudo obtener el túnel ngrok. Revisá /tmp/ngrok.log"
else
  echo "🌐 Tu endpoint público ngrok es: $NGROK_URL"
fi

# 🚀 Iniciar Flask
flask run --host=0.0.0.0 --port=5000

