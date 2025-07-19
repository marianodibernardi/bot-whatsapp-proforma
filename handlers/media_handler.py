import uuid
import os
import requests
from flask import Response
from requests.auth import HTTPBasicAuth

from services.factura_processor import procesar_factura
from utils.logger import log
from utils.state_manager import get_state, set_state
from utils.context import user_session

# Estas credenciales las podés mover a variables de entorno más adelante
account_sid = 'ACb08036fde0ec3f76d3acc7e9985687cb'
auth_token = '87faa70744cd4c4154968c2e8cd3e281'

def handle_media_message(data):
    from_number_raw = data.get("From")
    from_number = from_number_raw.replace("whatsapp:", "")
    state = get_state(from_number)
    log(f"📥 Estado actual al recibir archivo: {state}")

    if data.get("MediaContentType0") != "application/pdf":
        reply = "📎 El archivo debe ser un PDF."
        set_state(from_number, "inicio")
        return Response(f"<Response><Message>{reply}</Message></Response>", mimetype="text/xml")

    if state != "esperando_factura_pdf":
        reply = "📎 Recibí un archivo, pero no lo estaba esperando. Escribí *hola* para comenzar."
        set_state(from_number, "inicio")
        return Response(f"<Response><Message>{reply}</Message></Response>", mimetype="text/xml")

    try:
        media_url = data["MediaUrl0"]
        log(f"📎 Descargando archivo desde: {media_url}")
        response = requests.get(media_url, auth=HTTPBasicAuth(account_sid, auth_token))

        nombre_archivo = f"static/facturas/{uuid.uuid4().hex}.pdf"
        with open(nombre_archivo, "wb") as f:
            f.write(response.content)

        resultado = procesar_factura(nombre_archivo)
        log(f"📊 Resultado: {resultado}")

        if "error" in resultado:
            reply = f"⚠️ Error al procesar factura: {resultado['error']}"
            set_state(from_number, "inicio")
        else:
            # Guardar datos extraídos en sesión
            user_session[from_number] = user_session.get(from_number, {})
            user_session[from_number]["factura_extraida"] = resultado

            # Armar resumen
            resumen = (
                "✅ Factura procesada correctamente:\n"
                f"• Tipo: {resultado.get('preTipoComprobante', '-')}\n"
                f"• Número: {resultado.get('prePuntoVenta', '-')} - {resultado.get('preComprobanteNumero', '-')}\n"
                f"• Fecha: {resultado.get('preFechaEmision', '-')}\n"
                f"• Importe total: ${resultado.get('preImporteTotal', '-')}\n"
                f"• CAE: {resultado.get('preNumeroCAE', '-')}\n\n"
                "¿Los datos están correctos?\n"
                "1️⃣ Sí, continuar\n"
                "2️⃣ No, quiero editar"
            )
            reply = resumen
            set_state(from_number, "esperando_confirmacion")



    except Exception as e:
        log(f"❌ Error procesando archivo: {str(e)}")
        reply = "❌ Hubo un error procesando el archivo. Intentá de nuevo."
    finally:
        if os.path.exists(nombre_archivo):
            os.remove(nombre_archivo)
        set_state(from_number, "inicio")

    return Response(f"<Response><Message>{reply}</Message></Response>", mimetype="text/xml")
