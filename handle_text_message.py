# handle_text_message.py

from utils.state_manager import get_state, set_state, get_selected_proforma
from utils.logger import log
from handlers.inicio import handle_inicio
from handlers.esperando_num_factura import handle_esperando_num_factura
from handlers.login_handler import handle_login
from handlers.codigo_handler import handle_codigo_verificacion
from handlers.seleccionar_usuario_handler import handle_seleccionar_usuario
from handlers.proformas_handler import handle_listado_proformas
from handlers.acciones_proformas import handle_accion_sobre_proforma
from handlers.seleccionar_proforma import handle_seleccionar_proforma
from handlers.confirmacion_datos_factura_handler import handle_confirmacion_factura
from utils.context import user_pending_action

STATE_ROUTER = {
    "inicio": handle_inicio,
    "login": handle_login,
    "esperando_num_factura": handle_esperando_num_factura,
    "esperando_codigo": handle_codigo_verificacion,
    "seleccionar_usuario": handle_seleccionar_usuario,
    "mostrar_listado_proformas": handle_listado_proformas,
    "esperando_seleccion_proforma": handle_seleccionar_proforma,
    "acciones_proforma": handle_accion_sobre_proforma,
    "esperando_confirmacion": handle_confirmacion_factura
}

def handle_text_message(message):
    from_number = message["from"]
    body = message.get("text", {}).get("body", "").strip().lower()
    
    log(f"📩 Mensaje recibido de {from_number}: {body}")

    if body == "hola":
        reply = (
            f"👋 ¡Hola! ¿Qué querés hacer?\n"
            "1️⃣ Ver proformas pendientes\n"
            "2️⃣ Consultar estado de una factura"
        )
        set_state(from_number, "inicio")
    else:
        state = get_state(from_number)

        if state == "inicio" and body == "1":
            user_pending_action[from_number] = "ver_proformas"
            reply = handle_login(from_number, body)

        elif state == "inicio" and body == "2":
            user_pending_action[from_number] = "consultar_factura"
            reply = handle_login(from_number, body)

        else:
            handler = STATE_ROUTER.get(state)
            if handler:
                reply = handler(from_number, body)
            else:
                reply = "❓ No entendí tu mensaje. Escribí *hola* para comenzar."
                set_state(from_number, "inicio")

    estado_actual = get_state(from_number)
    proforma_seleccionada = get_selected_proforma(from_number)
    log(f"📤 Respuesta enviada: {reply}")
    log(f"🔁 Estado actual del usuario: {estado_actual}")
    if proforma_seleccionada:
        log(f"📌 Proforma seleccionada: {proforma_seleccionada}")

    return reply  # Solo texto plano, será enviado por `enviar_respuesta()` en webhook.py
