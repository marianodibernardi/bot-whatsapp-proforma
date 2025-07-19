from utils.context import user_session
from utils.state_manager import set_state
from utils.router import ejecutar_accion_pendiente
from utils.logger import log

def handle_seleccionar_usuario(from_number, body):
    seleccion = body.strip()

    if not seleccion.isdigit():
        return "❌ Por favor, respondé con el número del usuario que querés seleccionar."

    indice = int(seleccion) - 1
    session = user_session.get(from_number)

    if not session or "usuarios" not in session:
        set_state(from_number, "inicio")
        return "⚠️ Ocurrió un error. Escribí *hola* para comenzar de nuevo."

    usuarios = session["usuarios"]

    if indice < 0 or indice >= len(usuarios):
        return "❌ Número inválido. Por favor, elegí una opción válida del listado."

    usuario_seleccionado = usuarios[indice]
    cuit = usuario_seleccionado["cuit"]

    log(f"✅ Usuario del grupo seleccionado: {usuario_seleccionado['nombre']} (CUIT: {cuit})")

    # Guardamos solo el CUIT
    user_session[from_number] = {"cuit": cuit}

    return ejecutar_accion_pendiente(from_number)
