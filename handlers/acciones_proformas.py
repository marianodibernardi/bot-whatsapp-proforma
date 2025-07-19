from utils.state_manager import set_state
from utils.context import user_session

def handle_accion_sobre_proforma(from_number, body):
    if body == "1":
        # Acción: Asociar factura (pasar al siguiente estado)
        set_state(from_number, "esperando_factura_pdf")
        return "📤 Por favor, enviá el PDF de la factura para asociarla a la proforma seleccionada."

    elif body == "2":
        # Acción: Volver al listado
        set_state(from_number, "mostrar_listado_proformas")
        return "🔁 Volviendo al listado de proformas...\n"  # El estado se manejará por el test_console

    else:
        return "❓ Opción no válida. Respondé con *1* o *2*."
