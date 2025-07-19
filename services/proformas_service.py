from services.sqlserver_client import get_connection
from utils.logger import log

def obtener_proformas_por_cuit(cuit):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("EXEC sp_get_proformas_por_cuit ?", cuit)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        log(f"❌ Error al obtener proformas: {e}")
        return []
