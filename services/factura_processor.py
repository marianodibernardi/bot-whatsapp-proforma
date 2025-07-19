import os
import json
import time
import base64
import pdfplumber
#import fitz  # PyMuPDF
import requests
import openai
##import openai.error

# 🔐 Clave de OpenAI
openai.api_key =  os.getenv("OPENAI_API_KEY")

# 📌 URL de la API de ARCA
API_ARCA = os.getenv("API_ARCA")

# 📁 Carpeta donde están los PDFs
CARPETA_FACTURAS = "facturas"

# 🧠 Prompt COMPLETO para OpenAI
PROMPT_FACTURA = (
    "Sos un sistema experto en extracción de datos desde texto plano de facturas PDF. "
    "Debés responder EXCLUSIVAMENTE con un objeto JSON plano, parseable, sin ningún texto adicional.\n\n"
    "Campos requeridos:\n"
    "- preTipoComprobante: código numérico según AFIP (1 = Factura A, 6 = Factura B, etc.).\n"
    "- preFechaEmision: fecha en formato DD-MM-YYYY.\n"
    "- prePuntoVenta: primeros 5 dígitos del número de factura, con ceros a la izquierda (ej: '00003'). Siempre devolver como string de 5 caracteres.\n"
    "- preComprobanteNumero: últimos 8 dígitos del número de factura (ej: '00005587'). Siempre devolver como string de 8 caracteres.\n"
    "- preFechaVencimiento: si no está explícita, usar el mismo valor de preFechaEmision.\n"
    "- preImporteGravado: subtotal sin IVA como número decimal. No usar símbolo $, ni separadores de miles. Usar punto decimal.\n"
    "- preImporteIVA: suma total de IVA como número decimal. Sin símbolo $, sin separadores de miles.\n"
    "- preImporteTotal: importe total final como número decimal. Sin símbolo $, sin separadores de miles.\n"
    "- preNumeroCAE: número CAE como string de 14 dígitos. Buscar palabras como 'CAE', 'N° CAE', 'CAE N°', etc., y tomar los 14 números que lo siguen. Si no se encuentra, devolver 'None'.\n"
    "- preVencimientoCAE: fecha de vencimiento del CAE en formato DD-MM-YYYY. Buscar expresiones como 'Vto CAE', 'Fecha de Vto CAE', etc. Si no se encuentra, devolver 'None'.\n"
    "- preObservaciones: texto libre (obra, OC, certificado, notas, etc.).\n"
    "- preCuiReceptor: Buscar el CUIT de KIR S.R.L. como '30-70223204-6' o '30702232046' en cualquier parte del texto. Si se encuentra, devolver '30702232046'. Si no se encuentra, devolver 'None'.\n"
    "- preCuitEmisor: Buscar todos los CUITs en el texto. Si hay uno que **no sea** '30-70223204-6' ni '30702232046', tomarlo como el CUIT del emisor. Generalmente aparece precedido por 'CUIT'. Devolverlo como string de 11 dígitos, sin guiones ni puntos. Si no se encuentra, devolver 'None'.\n\n"
    "⚠️ RESPONDÉ SÓLO CON UN JSON. NO:\n"
    "- NO uses etiquetas de código como ```json o markdown.\n"
    "- NO agregues comentarios, títulos, explicaciones ni encabezados.\n"
    "- NO infieras valores. Si no hay información, usá 'None'.\n"
    "- NO devuelvas texto fuera del JSON, ni antes ni después.\n\n"
    "📌 Requisitos de formato:\n"
    "- Todas las fechas deben estar en formato DD-MM-YYYY, con ceros si es necesario.\n"
    "- CUITs deben tener exactamente 11 dígitos numéricos, sin separadores.\n"
    "- preFechaVencimiento debe ser igual a preFechaEmision si no se encuentra otra explícita.\n"
    "- Todos los importes deben usar punto como separador decimal. No incluir separadores de miles ni símbolo de moneda.\n"
    "- El JSON debe ser válido, plano y parseable directamente por cualquier sistema.\n"
)

# ✅ Verifica si el texto pertenece a una factura ARCA
def es_factura_arca(texto):
    return "Esta Agencia no se responsabiliza por los datos ingresados en el detalle de la operación" in texto

# 📄 Extrae texto del PDF con PyMuPDF
def extraer_texto_pdf(path_pdf):
    texto = ""
    with pdfplumber.open(path_pdf) as pdf:
        for page in pdf.pages:
            texto += page.extract_text() or ""
    return texto

# 📎 Convierte PDF a base64
def pdf_a_base64(path_pdf):
    with open(path_pdf, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# 📤 Envía el PDF codificado a la API de ARCA
def llamar_api_arca(path_pdf):
    try:
        base64_pdf = pdf_a_base64(path_pdf)
        headers = {"Content-Type": "application/json"}
        body = {"archivo": base64_pdf}
        response = requests.post(API_ARCA, headers=headers, data=json.dumps(body))
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Error consultando API ARCA: {str(e)}"}

# 🤖 Llama a OpenAI con retry si no es ARCA
def llamar_openai(texto, max_retries=3):
    for intento in range(max_retries):
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": PROMPT_FACTURA},
                    {"role": "user", "content": texto[:10000]}
                ],
                temperature=0
            )
            respuesta = completion.choices[0].message.content.strip()
            return json.loads(respuesta)
        except openai.error.OpenAIError as e:
            if isinstance(e, openai.error.APIError) and e.http_status == 500 and intento < max_retries - 1:
                time.sleep(2 ** intento)
                continue
            return {"error": f"Error OpenAI: {str(e)}"}
        except Exception as e:
            return {"error": f"Error inesperado: {str(e)}"}
    return {"error": "Error persistente al llamar a OpenAI"}

# 🔁 Procesa UNA factura
def procesar_factura(path_pdf):
    texto = extraer_texto_pdf(path_pdf)
    if es_factura_arca(texto):
        return llamar_api_arca(path_pdf)
    else:
        return llamar_openai(texto)

# 🔄 Procesa todas las facturas de la carpeta
def main():
    for archivo in os.listdir(CARPETA_FACTURAS):
        if not archivo.lower().endswith(".pdf"):
            continue
        path = os.path.join(CARPETA_FACTURAS, archivo)
        print(f"\n📄 Procesando: {archivo}")
        resultado = procesar_factura(path)
        print(json.dumps(resultado, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
