from utils.context import user_pending_action
from utils.state_manager import set_state
from utils.logger import log

def ejecutar_accion_pendiente(from_number):
    accion = user_pending_action.pop(from_number, None)

    if accion:
        log(f"▶️ Ejecutando acción pendiente: {accion}")

        if accion == "ver_proformas":
            set_state(from_number, "mostrar_proformas")
            return "✅ Código verificado. 📄 Ahora podés ver tus proformas. Respondé con A, B o C."

        elif accion == "consultar_factura":
            set_state(from_number, "esperando_num_factura")
            return "✅ Código verificado. 🧾 Ingresá el número de factura que querés consultar."

    # fallback
    set_state(from_number, "inicio")
    return (
        "✅ Código verificado correctamente.\n"
        "¿Qué querés hacer?\n"
        "1️⃣ Ver proformas\n"
        "2️⃣ Consultar una factura"
    )
