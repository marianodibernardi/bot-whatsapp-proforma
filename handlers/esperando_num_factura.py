from utils.state_manager import set_state

def handle_esperando_num_factura(from_number, body):
    set_state(from_number, "inicio")
    return f"🔍 Buscando estado para la factura {body}... (en desarrollo)"
