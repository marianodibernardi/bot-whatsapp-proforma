from services.proformas_service import obtener_proformas_por_cuit
from utils.state_manager import set_state
from utils.context import user_session
from utils.logger import log

def handle_listado_proformas(from_number, body):
    session = user_session.get(from_number)
    if not session or "cuit" not in session:
        set_state(from_number, "inicio")
        return "⚠️ No pudimos acceder a tus proformas. Escribí *hola* para comenzar de nuevo."

    cuit = session["cuit"]
    proformas = obtener_proformas_por_cuit(cuit)

    if not proformas:
        return "📭 No tenés proformas disponibles."

    # Guardar proformas en sesión para permitir selección posterior
    session["proformas"] = proformas
    set_state(from_number, "esperando_seleccion_proforma")

    mensaje = "📄 Tus proformas:\n"
    for i, p in enumerate(proformas, start=1):
        mensaje += f"{i}. Nº {p['PROFO_NUMERO']} - ${p['PROFO_IMPORTE_TOTAL']:,.2f} - {p['Estado']}\n"

    mensaje += "\n✏️ Respondé con el número de la proforma que querés usar."
    return mensaje
