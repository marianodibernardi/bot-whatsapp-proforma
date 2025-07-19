# confirmacion_handler.py
from utils.context import user_session
from utils.state_manager import set_state
from utils.logger import log

def handle_confirmacion_factura(from_number, body):
    session = user_session.get(from_number)

    if not session or "factura_extraida" not in session:
        set_state(from_number, "inicio")
        return (
            "⚠️ No tengo una factura procesada reciente para confirmar.\n"
            "Por favor escribí *hola* para comenzar de nuevo."
        )

    respuesta = body.strip()

    if respuesta == "1":
        factura = session["factura_extraida"]

        # Acá podrías guardar la factura en base de datos o continuar con otro flujo
        log(f"✅ Factura confirmada por {from_number}: {factura}")

        set_state(from_number, "inicio")  # o podés continuar a otro paso si lo necesitás
        return "✅ ¡Perfecto! La factura fue confirmada. ¿Qué querés hacer ahora?\n1️⃣ Ver proformas\n2️⃣ Consultar otra factura"

    elif respuesta == "2":
        set_state(from_number, "formulario_edicion")
        return (
            "✏️ Vas a poder editar los campos manualmente.\n"
            "Hacé clic en el siguiente enlace para completar los datos faltantes:"
            "\n🌐 https://tuapp.com/editar_factura?user={}".format(from_number)
        )

    else:
        return "❓ Opción inválida. Respondé con 1 para confirmar o 2 para editar."
