from utils.state_manager import set_state

def handle_inicio(from_number, body):
    if body == "1":
        reply = (
            "📋 Estas son tus proformas disponibles:\n"
            "A️⃣ Proforma A123 - $120.000 - 01/07/2025\n"
            "B️⃣ Proforma B456 - $240.000 - 05/07/2025\n"
            "C️⃣ Proforma C789 - $180.000 - 08/07/2025\n\n"
            "Respondé con A, B o C para continuar."
        )
        set_state(from_number, "mostrar_proformas")
    elif body == "2":
        reply = "🧾 Indicame el número de factura."
        set_state(from_number, "esperando_num_factura")
    elif body == "3":
        reply = "👨‍💼 Un agente se pondrá en contacto con vos."
        set_state(from_number, "inicio")
    else:
        reply = "❓ Opción no válida. Escribí *hola* para comenzar."
        set_state(from_number, "inicio")
    return reply
