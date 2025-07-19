from utils.context import user_session
from utils.state_manager import set_state
from utils.logger import log

def handle_seleccionar_proforma(from_number, body):
    session = user_session.get(from_number)

    if not session or "proformas" not in session:
        set_state(from_number, "inicio")
        return "⚠️ No hay proformas disponibles. Escribí *hola* para comenzar de nuevo."

    if not body.isdigit():
        return "❌ Por favor escribí el número de la proforma que querés seleccionar."

    idx = int(body) - 1
    proformas = session["proformas"]

    if idx < 0 or idx >= len(proformas):
        return "❌ Número fuera de rango. Elegí un número válido del listado."

    proforma = proformas[idx]
    session["profo_codigo"] = proforma["PROFO_CODIGO"]
    set_state(from_number, "acciones_proforma")

    return (
        f"📄 Proforma Nº {proforma['PROFO_NUMERO']} seleccionada.\n"
        "¿Qué querés hacer?\n"
        "1️⃣ Asociar factura\n"
        "2️⃣ Volver al listado"
    )
