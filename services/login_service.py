import random 
from services.sqlserver_client import get_connection
from utils.logger import log

def buscar_email_y_nombre_por_telefono(telefono_e164):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        email_resultado = ''
        origen = ''
        nombre = ''

        cursor.execute("""
            DECLARE @email VARCHAR(100), @origen VARCHAR(20), @nombre VARCHAR(100);
            EXEC sp_get_email_por_telefono ?, @email OUTPUT, @origen OUTPUT, @nombre OUTPUT;
            SELECT @email, @origen, @nombre;
        """, telefono_e164)

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "email": row[0],
                "origen": row[1],
                "nombre": row[2]
            }
        else:
            return None

    except Exception as e:
        log(f"❌ Error al ejecutar login_service: {e}")
        return None
    
def generar_codigo_verificacion():
    return random.randint(10000, 99999)

def guardar_codigo_verificacion(origen, email, codigo):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        if origen == "USUARIO":
            cursor.execute("""
                UPDATE BOT_USUARIOS_APP
                SET UAPP_COD_VERIFICACION = ?
                WHERE UAPP_EMAIL = ?
            """, codigo, email)
        elif origen == "GRUPO":
            cursor.execute("""
                UPDATE BOT_GRUPOS_USUARIOS_APP_TELEFONOS
                SET GPOAPPNUM_CODIGO_VERIFICACION = ?
                WHERE EMAIL = ?
            """, codigo, email)
        else:
            log("🚫 No se guarda el código: origen desconocido o no encontrado.")
            return False

        conn.commit()
        conn.close()

        log(f"✅ Código {codigo} guardado para email {email} (origen: {origen})")
        return True

    except Exception as e:
        log(f"❌ Error al guardar código de verificación: {e}")
        return False
    

def validar_codigo_ingresado(origen, email, codigo_ingresado):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        if origen == "USUARIO":
            cursor.execute("""
                SELECT UAPP_COD_VERIFICACION
                FROM BOT_USUARIOS_APP
                WHERE UAPP_EMAIL = ?
            """, email)
        elif origen == "GRUPO":
            cursor.execute("""
                SELECT GPOAPPNUM_CODIGO_VERIFICACION
                FROM BOT_GRUPOS_USUARIOS_APP_TELEFONOS
                WHERE EMAIL = ?
            """, email)
        else:
            log("❌ Origen inválido para validar código.")
            return False

        row = cursor.fetchone()
        conn.close()

        if row and str(row[0]) == str(codigo_ingresado):
            return True
        else:
            return False

    except Exception as e:
        log(f"❌ Error al validar código de verificación: {e}")
        return False




def obtener_cuit_post_login( email,origen):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        if origen == "USUARIO":
            cursor.execute("""
                SELECT UAPP_CUIT
                FROM BOT_USUARIOS_APP
                WHERE UAPP_EMAIL = ?
            """, email)

            row = cursor.fetchone()
            conn.close()

            if row:
                return {"tipo": "USUARIO", "cuit": row[0]}
            else:
                return {"tipo": "USUARIO", "cuit": None}  # Usuario no encontrado

        elif origen == "GRUPO":
            cursor.execute("""
                SELECT GPOAPP_CODIGO
                FROM BOT_GRUPOS_USUARIOS_APP_TELEFONOS
                WHERE EMAIL = ?
            """, email)

            row = cursor.fetchone()
            if not row:
                conn.close()
                return {"tipo": "GRUPO", "usuarios": []}  # Grupo sin usuarios

            gpoapp_codigo = row[0]

            cursor.execute("""
                SELECT UAPP_CUIT, UAPP_NOMBRE
                FROM BOT_USUARIOS_APP
                WHERE GPOAPP_CODIGO = ?
            """, gpoapp_codigo)

            rows = cursor.fetchall()
            conn.close()

            usuarios = [
                {"cuit": r[0], "nombre": r[1]} for r in rows
            ]
            return {"tipo": "GRUPO", "usuarios": usuarios, "gpoapp_codigo": gpoapp_codigo}

        else:
            return {"tipo": "NO_DEFINIDO"}

    except Exception as e:
        log(f"❌ Error al obtener CUIT post-login: {e}")
        return {"tipo": "ERROR"}
