import os
import uuid
import requests
from utils.logger import log
from utils.state_manager import get_state, set_state
from utils.context import user_session
from services.factura_processor import procesar_factura

def handle_media_message(message, access_token):
    from_number = message["from"]
    state = get_state(from_number)
    log(f"📥 Estado actual al recibir archivo: {state}")

    # Solo aceptamos PDF enviados como documentos
    if message.get("type") != "document" or message["document"].get("mime_type") != "application/pdf":
        reply = "📎 El archivo debe ser un PDF adjunto como documento."
        set_state(from_number, "inicio")
        return reply

    if state != "esperando_factura_pdf":
        reply = "📎 Recibí un archivo, pero no lo estaba esperando. Escribí *hola* para comenzar."
        set_state(from_number, "inicio")
        return reply

    try:
        media_id = message["document"]["id"]
        log(f"📎 Media ID recibido: {media_id}")

        # Paso 1: Obtener la URL de descarga desde la Graph API
        url_info = f"https://graph.facebook.com/v19.0/{media_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        res_info = requests.get(url_info, headers=headers)
        media_url = res_info.json().get("url")
        if not media_url:
            raise Exception("No se pudo obtener la URL del archivo.")

        # Paso 2: Descargar el archivo usando esa URL
        res_file = requests.get(media_url, headers=headers)
        nombre_archivo = f"static/facturas/{uuid.uuid4().hex}.pdf"
        with open(nombre_archivo, "wb") as f:
            f.write(res_file.content)

        # Paso 3: Procesar factura
        resultado = procesar_factura(nombre_archivo)
        log(f"📊 Resultado: {resultado}")

        if "error" in resultado:
            reply = f"⚠️ Error al procesar factura: {resultado['error']}"
            set_state(from_number, "inicio")
        else:
            # Guardar datos extraídos
            user_session[from_number] = user_session.get(from_number, {})
            user_session[from_number]["factura_extraida"] = resultado

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
        set_state(from_number, "inicio")
    finally:
        if "nombre_archivo" in locals() and os.path.exists(nombre_archivo):
            os.remove(nombre_archivo)

    return reply  # Retorna solo texto plano para que webhook.py lo envíe
