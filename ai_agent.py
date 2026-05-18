import google.generativeai as genai
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

def check_local_llm():
    """
    Verifica si el servidor local de LM Studio está activo en el puerto 1234.
    """
    try:
        response = requests.get("http://localhost:1234/v1/models", timeout=1)
        if response.status_code == 200:
            return True
    except:
        pass
    return False

def query_local_llm(prompt):
    """
    Realiza una consulta al servidor local de LM Studio (Gemma 4).
    """
    url = "http://localhost:1234/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    payload = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f">> [IA Local] Error al consultar LM Studio: {e}")
    return None

def calificar_prospecto(mensaje):
    """
    Analiza el mensaje del cliente con IA para determinar su nivel de interés.
    Intenta usar LM Studio (Gemma 4 local) y cae a Gemini Cloud de respaldo.
    """
    prompt = (
        f"Analiza este mensaje de un prospecto de Gano Excel: '{mensaje}'. "
        f"Clasifica su nivel de interés en una sola palabra: 'Bajo', 'Medio' o 'Alto'. "
        f"Considera 'Alto' si pregunta por precios, afiliación o productos específicos. "
        f"Responde ÚNICAMENTE con una de las tres palabras sin texto adicional ni asteriscos."
    )

    if check_local_llm():
        print(">> [IA] Servidor Local LM Studio DETECTADO. Procesando con Gemma 4...")
        resultado = query_local_llm(prompt)
        if resultado:
            interes = resultado.strip().replace("*", "").replace(".", "")
            if interes in ["Bajo", "Medio", "Alto"]:
                return interes
            for word in ["Alto", "Medio", "Bajo"]:
                if word in interes:
                    return word

    # Fallback a Gemini Cloud
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Bajo"

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    try:
        response = model.generate_content(prompt)
        interes = response.text.strip().replace("*", "").replace(".", "")
        return interes if interes in ["Bajo", "Medio", "Alto"] else "Bajo"
    except Exception as e:
        print(f"Error calificador Gemini Cloud: {e}")
        return "Bajo"

def generar_copy_ia(id_publicacion, whatsapp_phone, custom_store_url=None):
    """
    Genera un texto persuasivo (copywriting) para redes sociales usando Gemini o Gemma 4 Local.
    """
    # Determinar categoría buscando en contenido_ganoderma.json
    categoria = "bienestar"
    try:
        if os.path.exists("contenido_ganoderma.json"):
            with open("contenido_ganoderma.json", "r", encoding="utf-8") as file:
                contenido = json.load(file)
                for post in contenido:
                    if post.get("id") == id_publicacion:
                        categoria = post.get("categoria_imagen", "bienestar")
                        break
    except Exception as e:
        print(f">> [IA] Error al leer la categoría del post: {e}")

    # Ajustar el enfoque según la categoría del post alineado con los 4 Pilares Oficiales de Gano iTouch Peru
    if categoria in ["bebibles", "clasico", "bebidas"]:
        system_context = (
            "Eres un experto en Marketing de Afiliados y copywriter profesional para Gano Excel / Gano iTouch.\n"
            "Tu objetivo es redactar un post persuasivo de Facebook enfocado en el pilar oficial ⚡ ENERGIZA (Energiza).\n"
            "Vende las bebidas premium enriquecidas con Ganoderma Lucidum (Café 3 en 1, Café Classic negro o Chocolate).\n"
            "Enfatiza la vitalidad natural sostenida, el enfoque mental, el rendimiento físico diario y la delicia del café gourmet sin sufrir taquicardia ni nerviosismo.\n"
        )
    elif categoria == "salud":
        system_context = (
            "Eres un experto en Marketing de Afiliados y copywriter profesional para Gano Excel / Gano iTouch.\n"
            "Tu objetivo es redactar un post persuasivo de Facebook enfocado en los pilares oficiales ➕ REVITALIZA (Revitaliza) y 💜 ARMONIZA (Armoniza).\n"
            "Enfatiza el poder del extracto 100% soluble de Ganoderma Lucidum para la nutrición celular profunda, el fortalecimiento activo del sistema inmunológico (defensas) y el equilibrio corporal que ayuda a mitigar el estrés y conseguir paz mental y descanso reparador.\n"
        )
    elif categoria == "negocio":
        system_context = (
            "Eres un experto en Marketing de Afiliados y copywriter profesional para Gano Excel / Gano iTouch.\n"
            "Tu objetivo es redactar un post de Facebook persuasivo enfocado en el pilar oficial 💬 SOCIALIZA (Socializa) y la prosperidad comunitaria.\n"
            "Invita a las personas a emprender con Network Marketing, compartiendo bienestar y construyendo una red de residuales sólida desde casa que les brinde verdadera libertad financiera con el respaldo de Gano Excel.\n"
        )
    else:
        system_context = (
            "Eres un experto en Marketing de Afiliados y copywriter profesional para Gano Excel / Gano iTouch.\n"
            "Tu objetivo es redactar un post persuasivo de Facebook alineado con los 4 Pilares Corporativos Oficiales: ⚡ ENERGIZA, ➕ REVITALIZA, 💜 ARMONIZA y 💬 SOCIALIZA.\n"
        )

    # Restricciones éticas (Evitar claims de curación de enfermedades graves para cumplir regulaciones)
    system_context += (
        "RESTRICCIÓN ÉTICA ABSOLUTA: Evita promesas médicas curativas falsas o Claims como decir que cura el cáncer, diabetes, etc.\n"
        "En su lugar, usa un lenguaje de 'refuerzos inmunológicos lícitos', vitalidad, energía, nutrición celular profunda y antioxidantes con una matriz Sinergista.\n"
        "Formato del post:\n"
        "- Comienza con un hook/llamado a la acción impactante con emojis.\n"
        "- Explica 3 beneficios clave de forma muy atractiva y concisa.\n"
        "- Termina con un llamado a la acción claro para comprar online o enviar un mensaje.\n"
        "- Escribe con tono enérgico, inspirador y profesional.\n"
        "- Incluye hashtags estratégicos y mantén el texto relativamente corto pero muy persuasivo.\n"
    )

    # Enlace de la tienda
    if custom_store_url:
        store_url = custom_store_url
    else:
        store_name = os.getenv("GANO_ITOUCH_STORE", "joherobacafe")
        store_url = f"https://peru.ganoitouch.biz/{store_name}"
    
    prompt = (
        f"{system_context}\n"
        f"Por favor redacta la publicación correspondiente para el ID '{id_publicacion}' (Categoría: {categoria}).\n"
        f"Asegúrate de incluir de forma natural el enlace a mi tienda oficial de afiliado al final:\n"
        f"👉 {store_url}\n"
        f"Y menciona que pueden escribirme al WhatsApp: +{whatsapp_phone} si tienen dudas.\n"
        f"Responde únicamente con el texto completo del post finalizado, listo para copiar y pegar, sin explicaciones ni notas adicionales."
    )

    # Definir texto alternativo/fallback si falla todo
    if categoria == "negocio":
        fallback_text = (
            "¿Y si tu bebida de cada mañana comenzara a pagarte grandes dividendos? 📈☕\n"
            "Construye autonomía financiera y genera ingresos residuales desde la comodidad de tu hogar asociándote con un gigante mundial del bienestar.\n\n"
            "👉 Conviértete en distribuidor y empieza a crecer hoy mismo:\n"
            f"🔗 {store_url}\n\n"
            f"O escríbeme directamente al WhatsApp (+{whatsapp_phone}) para darte todos los detalles de la duplicación comercial. 🚀"
        )
    else:
        fallback_text = (
            "¡Dale a tu cuerpo el escudo natural que se merece! 🛡️🍄\n"
            "Empieza tus mañanas llenándote de energía real y antioxidantes profundos gracias a las infusiones enriquecidas con Ganoderma Lucidum soluble de Gano Excel.\n\n"
            "👉 Pídelo 100% seguro en mi portal oficial y recíbelo en casa:\n"
            f"🔗 {store_url}\n\n"
            f"Dudas o pedidos rápidos al WhatsApp (+{whatsapp_phone}). ¡Sabor y vitalidad garantizada! ☕✨"
        )

    # 1. Intentar con LM Studio (Gemma 4 local)
    if check_local_llm():
        print(">> [IA] Servidor Local LM Studio DETECTADO. Generando copy con Gemma 4...")
        resultado = query_local_llm(prompt)
        if resultado:
            return resultado

    # 2. Fallback a Gemini Cloud
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print(">> [IA] Error: No se encontró GEMINI_API_KEY en el entorno y LM Studio no responde. Usando texto de respaldo...")
        return fallback_text

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    try:
        # Timeout de 15 segundos para evitar bloqueos de red indefinidos
        response = model.generate_content(
            prompt,
            request_options={"timeout": 15.0}
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error al generar copy con Gemini Cloud: {e}. Usando texto de respaldo...")
        return fallback_text

def generar_copy_personalizado_ia(prompt_usuario, whatsapp_phone, custom_store_url=None):
    """
    Genera un texto persuasivo personalizado basado en un prompt del usuario,
    respetando los lineamientos de la marca y agregando los enlaces oficiales de afiliado.
    """
    system_context = (
        "Eres un experto en Marketing de Afiliados y copywriter profesional para Gano Excel / Gano iTouch.\n"
        "El usuario te ha dado la siguiente instrucción específica para su publicación:\n"
        f"Instrucción del usuario: '{prompt_usuario}'\n\n"
        "RESTRICCIÓN ÉTICA ABSOLUTA: Evita promesas médicas curativas falsas o Claims como decir que cura el cáncer, diabetes, etc. Usa un lenguaje de bienestar lícito y antioxidantes.\n"
        "Formato del post:\n"
        "- Comienza con un hook impactante con emojis.\n"
        "- Desarrolla la idea del usuario de forma persuasiva y estructurada.\n"
        "- Termina con un llamado a la acción claro.\n"
        "- Escribe con tono enérgico, inspirador y profesional.\n"
    )
    
    if custom_store_url:
        store_url = custom_store_url
    else:
        store_name = os.getenv("GANO_ITOUCH_STORE", "joherobacafe")
        store_url = f"https://peru.ganoitouch.biz/{store_name}"
        
    prompt = (
        f"{system_context}\n"
        f"Por favor redacta la publicación basada en la instrucción del usuario.\n"
        f"Asegúrate de incluir de forma natural el enlace a mi tienda oficial de afiliado al final:\n"
        f"👉 {store_url}\n"
        f"Y menciona que pueden escribirme al WhatsApp: +{whatsapp_phone} si tienen dudas.\n"
        f"Responde únicamente con el texto completo del post finalizado, listo para copiar y pegar, sin notas ni explicaciones."
    )
    
    fallback_text = (
        f"¡Bienvenido al bienestar absoluto! ☕✨\n\n"
        f"Basado en tu idea: '{prompt_usuario}'.\n\n"
        f"👉 Adquiere tus infusiones favoritas de Ganoderma Lucidum en mi portal oficial de afiliado:\n"
        f"🔗 {store_url}\n\n"
        f"Consultas personalizadas al WhatsApp: +{whatsapp_phone}"
    )

    if check_local_llm():
        resultado = query_local_llm(prompt)
        if resultado:
            return resultado

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return fallback_text

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    try:
        response = model.generate_content(prompt, request_options={"timeout": 15.0})
        return response.text.strip()
    except Exception as e:
        print(f"Error generando copy personalizado: {e}")
        return fallback_text

def generar_invitacion_cafecito_ia(nombre_prospecto, distancia_metros, whatsapp_phone, custom_store_url=None):
    """
    Genera un mensaje de invitación de café (One-to-One) súper casual, amigable y persuasivo,
    adaptado por geolocalización.
    """
    system_context = (
        "Eres un networker profesional y sumamente simpático de Gano iTouch.\n"
        f"Tu objetivo es redactar un mensaje corto y casual de WhatsApp para invitar a '{nombre_prospecto}', "
        f"quien se encuentra muy cerca (a unos {distancia_metros} metros) en este momento, a tomar un café clásico o 3en1 saludable "
        "para compartir una oportunidad de negocio rápida de forma amigable, relajada y sin presión comercial agresiva.\n\n"
        "RESTRICCIÓN ÉTICA: Tono conversacional, fresco, directo y muy natural de amigos que se cruzan en la calle."
    )
    
    if custom_store_url:
        store_url = custom_store_url
    else:
        store_name = os.getenv("GANO_ITOUCH_STORE", "joherobacafe")
        store_url = f"https://peru.ganoitouch.biz/{store_name}"
        
    prompt = (
        f"{system_context}\n"
        f"Redacta un mensaje de no más de 3-4 líneas listo para enviar por WhatsApp.\n"
        f"Incluye de forma muy casual y opcional que si quiere ver de qué trata de antemano, puede ver tu portal virtual:\n"
        f"🔗 {store_url}\n"
        f"Responde únicamente con el texto del mensaje listo para enviar, sin notas, ni comillas ni explicaciones."
    )
    
    fallback_text = (
        f"¡Hola {nombre_prospecto}! ¿Cómo estás? Qué gusto saludarte. ☕️\n\n"
        f"Casualmente estoy muy cerca de ti, por esta zona. Tengo un ratito libre y me encantaría invitarte un café gourmet enriquecido con Ganoderma para conversar de un proyecto de negocio genial.\n\n"
        f"Si quieres echarle un ojo antes, mira mi portal: {store_url} \n"
        f"Avisame y nos encontramos en 10 minutos. ¡Un abrazo!"
    )

    if check_local_llm():
        resultado = query_local_llm(prompt)
        if resultado:
            return resultado

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return fallback_text

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    try:
        response = model.generate_content(prompt, request_options={"timeout": 15.0})
        return response.text.strip()
    except Exception as e:
        print(f"Error generando invitacion cafecito: {e}")
        return fallback_text

if __name__ == "__main__":
    # Prueba rápida con codificación de consola segura
    import sys
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
    
    print("Verificando soporte local de LM Studio (Gemma 4)...")
    if check_local_llm():
        print(">> [✓] ¡Servidor Local LM Studio activo en puerto 1234!")
    else:
        print(">> [x] Servidor Local LM Studio no disponible (usando Gemini Cloud de respaldo).")

    copy_text = generar_copy_ia("publicacion_06", "51999122333")
    print("\nTest Copy:\n", copy_text)
    print("\nTest Scoring:", calificar_prospecto("Hola, ¿cuánto cuesta el paquete ESP3 para afiliarme?"))

