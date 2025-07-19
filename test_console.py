# test_console.py
from handle_text_message import handle_text_message

if __name__ == "__main__":
    print("💬 Simulador de conversación con el bot (escribí 'salir' para salir)")
    from_number = input("📱 Ingresá el número E.164 del usuario (ej: +5493544542532): ").strip()
    while True:
        user_input = input("🧑 Vos: ")
        if user_input.strip().lower() in ("exit", "salir"):
            break
        data = { "From": f"whatsapp:{from_number}", "Body": user_input }
        handle_text_message(data, modo_local=True)  # 👈 Modo consola activado
