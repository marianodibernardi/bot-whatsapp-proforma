from services.login_service import (
    buscar_email_y_nombre_por_telefono,
    generar_codigo_verificacion,
    guardar_codigo_verificacion
)
from utils.logger import log
from utils.state_manager import set_state
from utils.context import user_pending_action, user_session

def handle_login(from_number, body):
    log(f"🔐 Ejecutando validación para {from_number}")
    resultado = buscar_email_y_nombre_por_telefono(from_number)

    if resultado is None or resultado["origen"] == "NO_ENCONTRADO":
        log("🔐 Usuario no encontrado")
        return (
            "🚫 Tu número no se encuentra asociado a ningún usuario registrado.\n"
            "Si creés que esto es un error, por favor contactá al administrador del sistema."
        )

    nombre = resultado["nombre"]
    primer_nombre = nombre.split()[0] if nombre else ""
    email = resultado["email"]
    origen = resultado["origen"]

    user_session[from_number] = {
        "email": email,
        "origen": origen
    }

    codigo = generar_codigo_verificacion()
    guardar_ok = guardar_codigo_verificacion(origen, email, codigo)

    if not guardar_ok:
        return "⚠️ No pudimos generar tu código de verificación. Intentá más tarde o contactá a un administrador."

    log(f"🔓 Código generado ({codigo}) para {origen}: {email}")

    accion = user_pending_action.get(from_number)
    set_state(from_number, "esperando_codigo", selected_proforma=accion)

    return (
        f"👋 Hola {primer_nombre}!\n"
        f"Antes de continuar, vamos a validar tu identidad.\n"
        f"Te enviamos un código de verificación a la casilla *{email}*.\n"
        "📩 Revisá tu correo e ingresá el código aquí para continuar."
    )
