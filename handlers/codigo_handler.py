from services.login_service import validar_codigo_ingresado, obtener_cuit_post_login
from utils.logger import log
from utils.state_manager import set_state
from utils.context import user_session
from handlers.proformas_handler import handle_listado_proformas

def handle_codigo_verificacion(from_number, body):
    codigo_ingresado = body.strip()

    # 1. Validación de formato
    if not codigo_ingresado.isdigit() or len(codigo_ingresado) != 5:
        return "❌ El código debe tener 5 dígitos numéricos. Probá de nuevo."

    # 2. Obtener datos de sesión
    session = user_session.get(from_number)

    if not session:
        log("⚠️ No se encontró información de sesión para validar el código.")
        set_state(from_number, "inicio")
        return (
            "⚠️ Ocurrió un error al validar tu identidad.\n"
            "Por favor escribí *hola* para comenzar de nuevo."
        )

    email = session["email"]
    origen = session["origen"]

    # 3. Validar el código contra la base
    if validar_codigo_ingresado(origen, email, codigo_ingresado):
        log(f"✅ Código válido para {from_number} ({email})")

        # 4. Obtener datos adicionales post validación
        resultado = obtener_cuit_post_login(email, origen)

        if not resultado:
            set_state(from_number, "inicio")
            return "⚠️ No se pudo continuar con la autenticación."

        log(f"🔎 Resultado post login: {resultado}")

        if origen == "USUARIO":
            # Agregar CUIT a la sesión existente
            session["cuit"] = resultado["cuit"]
            session["proformas"] = resultado.get("proformas", [])
            user_session[from_number] = session

            set_state(from_number, "mostrar_listado_proformas")
            return handle_listado_proformas(from_number, "")

        elif origen == "GRUPO":
            # Reemplazamos la sesión con info del grupo
            user_session[from_number] = {
                "grupo_codigo": resultado["gpoapp_codigo"],
                "usuarios": resultado["usuarios"]
            }
            set_state(from_number, "seleccionar_usuario")

            mensaje = "📋 Usuarios disponibles:"
            for i, usuario in enumerate(resultado["usuarios"], start=1):
                mensaje += f"\n{i}. {usuario['nombre']} ({usuario['email']})"
            mensaje += "\n\n✏️ Escribí el número del usuario que querés usar."
            return mensaje

    else:
        log(f"❌ Código incorrecto para {from_number}")
        return "❌ El código ingresado no es válido. Revisá tu correo e intentá nuevamente."
