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

def analizar_composicion_ia(img_ruta):
    """
    Analiza de forma multimodal la composición de la imagen para determinar el espacio negativo libre,
    los textos preexistentes, rostros o productos, y sugiere el mejor diseño, posición de texto
    y opacidad para la tarjeta de Gano iTouch.
    Utiliza un archivo de caché local (composicion_cache.json) para evitar consumir la cuota de la API
    de Gemini en ejecuciones repetidas y acelerar el renderizado.
    """
    nombre_archivo = os.path.basename(img_ruta)
    
    # 1. Cargar caché si existe
    ruta_cache = "composicion_cache.json"
    cache = {}
    if os.path.exists(ruta_cache):
        try:
            with open(ruta_cache, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except Exception as e:
            print(f">> [IA Visual] Error al leer caché: {e}")
            
    # Si ya está analizada esta imagen, retornar el resultado de inmediato
    if nombre_archivo in cache:
        print(f">> [IA Visual] [Cache OK] Recuperada composición guardada para {nombre_archivo}: {cache[nombre_archivo]}")
        return cache[nombre_archivo]
        
    fallback = {
        "region_libre": "bottom",
        "dibujar_placa": True,
        "color_texto": "white",
        "placa_opacity": 160,
        "estilo_sugerido": "DISENO_CRISTAL"
    }
    
    # En caso de rate limit o falta de API_KEY, si hay un valor pre-mapeado estático para los assets oficiales conocidos:
    mapeo_estatico = {
        "producto_jabon.jpg": {
            "region_libre": "center",
            "dibujar_placa": true,
            "color_texto": "white",
            "placa_opacity": 95,
            "estilo_sugerido": "DISENO_CRISTAL"
        },
        "producto_chocolate.jpg": {
            "region_libre": "center",
            "dibujar_placa": true,
            "color_texto": "white",
            "placa_opacity": 100,
            "estilo_sugerido": "DISENO_CRISTAL"
        },
        "producto_3en1.jpg": {
            "region_libre": "center",
            "dibujar_placa": true,
            "color_texto": "white",
            "placa_opacity": 100,
            "estilo_sugerido": "DISENO_CRISTAL"
        },
        "onetoone_es.jpg": {
            "region_libre": "bottom",
            "dibujar_placa": false,
            "color_texto": "black",
            "placa_opacity": 0,
            "estilo_sugerido": "DISENO_MINIMALISTA"
        },
        "onetoone_en.jpg": {
            "region_libre": "bottom",
            "dibujar_placa": false,
            "color_texto": "black",
            "placa_opacity": 0,
            "estilo_sugerido": "DISENO_MINIMALISTA"
        },
        "mr_leow3.jpg": {
            "region_libre": "bottom",
            "dibujar_placa": true,
            "color_texto": "white",
            "placa_opacity": 100,
            "estilo_sugerido": "DISENO_CRISTAL"
        }
    }
    
    # Si la imagen coincide con una conocida y no tenemos quota, podemos usar el fallback inteligente pre-diseñado
    if nombre_archivo in mapeo_estatico:
        fallback = mapeo_estatico[nombre_archivo]
        
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return fallback
        
    try:
        from PIL import Image
        import google.generativeai as genai
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        img = Image.open(img_ruta)
        
        # Optimización multimodal: Redimensionar imagen para reducir dramáticamente el peso de red y evitar timeouts 504.
        img_temp = img.copy()
        img_temp.thumbnail((300, 600), Image.Resampling.LANCZOS)
        
        prompt = (
            "Analiza esta imagen publicitaria de Gano iTouch/Gano Excel. "
            "Necesitamos superponer un texto nuevo en un recuadro o placa de forma ultra profesional. "
            "Para evitar arruinar el diseño, tapar el producto físico principal, rostros de personas, "
            "o textos preexistentes (como logos o nombres de producto ya impresos en la imagen), indícame: "
            "1. ¿En qué región de la imagen hay 'espacio vacío o negativo' libre para colocar el texto sin tapar nada? "
            "   Opciones: 'top' (arriba), 'bottom' (abajo), 'center' (centro), 'left' (izquierda), 'right' (derecha).\n"
            "2. ¿Debemos dibujar una placa translúcida de fondo para que el texto sea legible? "
            "   (Responde true si el fondo es muy detallado o colorido, o false si es un espacio liso/homogéneo donde se puede escribir directo sin caja).\n"
            "3. ¿Qué color de texto contrastaría mejor? "
            "   (Responde 'white', 'black', o un color hexadecimal elegante acorde a la paleta de la imagen).\n"
            "4. ¿Cuál debería ser la opacidad de la placa translúcida? (de 0 a 255, p.ej. 160 para cristal oscuro, 80 para cristal muy suave, 0 para nada).\n"
            "5. ¿Qué estilo sugiere? "
            "   'DISENO_ROLEX' (filtro sutil en toda la imagen), 'DISENO_CRISTAL' (placa de cristal central), 'DISENO_MINIMALISTA' (texto limpio directo sobre espacio negativo sin cajas).\n\n"
            "Responde estrictamente en formato JSON válido con las siguientes llaves: "
            "\"region_libre\", \"dibujar_placa\", \"color_texto\", \"placa_opacity\", \"estilo_sugerido\". "
            "No incluyas explicaciones ni formato markdown de código ```json."
        )
        
        response = model.generate_content([prompt, img_temp], request_options={"timeout": 25.0})
        texto_res = response.text.strip()
        
        # Limpiar posible markdown
        if "```json" in texto_res:
            texto_res = texto_res.split("```json")[1].split("```")[0].strip()
        elif "```" in texto_res:
            texto_res = texto_res.split("```")[1].split("```")[0].strip()
            
        data = json.loads(texto_res)
        
        # Validar y limpiar llaves
        for key in fallback:
            if key not in data:
                data[key] = fallback[key]
                
        # Forzar tipos de datos correctos
        if not isinstance(data["dibujar_placa"], bool):
            data["dibujar_placa"] = data["dibujar_placa"] in [True, "true", "True"]
        data["placa_opacity"] = int(data["placa_opacity"])
        
        # Guardar en caché
        cache[nombre_archivo] = data
        try:
            with open(ruta_cache, "w", encoding="utf-8") as f:
                json.dump(cache, f, indent=4, ensure_ascii=False)
            print(f">> [IA Visual] [Caché Guardada] Composición registrada para {nombre_archivo}")
        except Exception as ce:
            print(f">> [IA Visual] Error al guardar caché: {ce}")
            
        print(f">> [IA Visual] Composición analizada con éxito para {nombre_archivo}: {data}")
        return data
        
    except Exception as e:
        print(f">> [IA Visual] Alerta en análisis multimodal: {e}. Usando composición de respaldo.")
        return fallback

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

def generar_copy_ia(id_publicacion, whatsapp_phone, custom_store_url=None, idioma="Español", zona="Mercado General"):
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
        f"IMPORTANTE Y OBLIGATORIO: El idioma estricto para redactar esta publicación es {idioma.upper()}. Adapta absolutamente todo el texto, el tono, los modismos y el enfoque cultural a la siguiente zona geográfica o mercado: {zona.upper()}.\n"
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
        f"Y es ESTRICTAMENTE OBLIGATORIO que incluyas este enlace clickable exacto para WhatsApp:\n"
        f"📲 https://wa.me/{whatsapp_phone.replace('+', '').replace(' ', '')}\n"
        f"Responde únicamente con el texto completo del post finalizado, listo para copiar y pegar, sin explicaciones ni notas adicionales."
    )

    # Definir texto alternativo/fallback si falla todo
    if categoria == "negocio":
        fallback_text = (
            "¿Y si tu bebida de cada mañana comenzara a pagarte grandes dividendos? 📈☕\n"
            "Construye autonomía financiera y genera ingresos residuales desde la comodidad de tu hogar asociándote con un gigante mundial del bienestar.\n\n"
            "👉 Conviértete en distribuidor y empieza a crecer hoy mismo:\n"
            f"🔗 {store_url}\n\n"
            f"O escríbeme directo haciendo clic aquí para darte los detalles:\n📲 https://wa.me/{whatsapp_phone.replace('+', '').replace(' ', '')} 🚀"
        )
    else:
        fallback_text = (
            "¡Dale a tu cuerpo el escudo natural que se merece! 🛡️🍄\n"
            "Empieza tus mañanas llenándote de energía real y antioxidantes profundos gracias a las infusiones enriquecidas con Ganoderma Lucidum soluble de Gano Excel.\n\n"
            "👉 Pídelo 100% seguro en mi portal oficial y recíbelo en casa:\n"
            f"🔗 {store_url}\n\n"
            f"Dudas o pedidos rápidos al WhatsApp haciendo clic aquí:\n📲 https://wa.me/{whatsapp_phone.replace('+', '').replace(' ', '')} ☕✨"
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

def generar_copy_personalizado_ia(prompt_usuario, whatsapp_phone, custom_store_url=None, idioma="Español", zona="Mercado General"):
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
        f"IMPORTANTE Y OBLIGATORIO: El idioma estricto para redactar esta publicación es {idioma.upper()}. Adapta absolutamente todo el texto, el tono, los modismos y el enfoque cultural a la siguiente zona geográfica o mercado: {zona.upper()}.\n"
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
        f"Y es ESTRICTAMENTE OBLIGATORIO que incluyas este enlace clickable exacto para WhatsApp:\n"
        f"📲 https://wa.me/{whatsapp_phone.replace('+', '').replace(' ', '')}\n"
        f"Responde únicamente con el texto completo del post finalizado, listo para copiar y pegar, sin notas ni explicaciones."
    )
    
    fallback_text = (
        f"¡Bienvenido al bienestar absoluto! ☕✨\n\n"
        f"Basado en tu idea: '{prompt_usuario}'.\n\n"
        f"👉 Adquiere tus infusiones favoritas de Ganoderma Lucidum en mi portal oficial de afiliado:\n"
        f"🔗 {store_url}\n\n"
        f"Consultas personalizadas haciendo clic aquí:\n📲 https://wa.me/{whatsapp_phone.replace('+', '').replace(' ', '')}"
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

def conversar_prospecto_ia(mensaje_nuevo, link_tienda=None, whatsapp=None, idioma="Español", zona="Latinoamérica", media_b64=None, tipo_media=None):
    """
    Simula una conversación en lenguaje natural, actuando como un asesor experto de Gano iTouch.
    Ahora también puede escuchar audios y ver imágenes enviadas por WhatsApp.
    """
    import os
    import database_manager
    
    # Extraer perfil del afiliado desde la matriz SQLite
    afiliado = None
    if whatsapp:
        afiliado = database_manager.obtener_afiliado(whatsapp)
        
    store_url = link_tienda if link_tienda else f"https://peru.ganoitouch.biz/{os.getenv('GANO_ITOUCH_STORE', 'joherobacafe')}"
    whatsapp_phone = whatsapp if whatsapp else os.getenv("WHATSAPP_PHONE", "51947347666")
    idioma_env = os.getenv("IDIOMA_PUBLICACION", idioma)
    zona_env = os.getenv("ZONA_GEOGRAFICA", zona)
    
    # Variables financieras por defecto o del afiliado
    tipo_cambio_actual = afiliado["tipo_cambio"] if afiliado else float(os.getenv("TIPO_CAMBIO", 3.85))
    cta_bcp_actual = afiliado["cta_bcp"] if afiliado and afiliado["cta_bcp"] else os.getenv("CTA_BCP", "Solicitar por interno")
    cta_interbank_actual = afiliado["cta_interbank"] if afiliado and afiliado["cta_interbank"] else os.getenv("CTA_INTERBANK", "Solicitar por interno")
    nombre_lider = afiliado["nombre"] if afiliado else os.getenv("FACEBOOK_PAGE_NAME", "Jorge Rodríguez")
    
    system_context = (
        f"Eres el asistente de Inteligencia Artificial oficial de {nombre_lider}, líder de Gano iTouch.\\n"
        "Tu objetivo principal es cerrar ventas y afiliaciones, actuando con muchísima empatía y profesionalismo.\\n"
        "Si el usuario envía una nota de voz, escúchala y respóndele por escrito de forma muy cálida.\\n\\n"
        "PROTOCOLOS DE CIERRE (MUY IMPORTANTE):\\n"
        "1. Si el prospecto quiere COMPRAR para recoger en Sede o AFILIARSE, tú debes guiarlo como si fueras un formulario interactivo.\\n"
        "2. Pídele amablemente que te envíe sus datos *POR ESCRITO* (Nombre completo, DNI, Correo, Celular y Sede de Recojo) "
        "y adicionalmente, por seguridad de Gano Excel, que mande una FOTO O PANTALLAZO DE SU DNI.\\n"
        "3. REGLAS FINANCIERAS Y DE PAGO:\\n"
        "   - Los precios de Gano iTouch están en DÓLARES (USD). "
        f"Multiplica por el tipo de cambio de {tipo_cambio_actual} para darle el precio exacto en SOLES (PEN).\\n"
        "   - **Para Compras Pequeñas (Paquetes Básicos):** Ofrécele pagar por Yape o Plin. "
        "Usa las etiquetas [ENVIAR_QR_YAPE] o [ENVIAR_QR_PLIN] para que el sistema le envíe la foto del QR. "
        f"Provee también el celular {whatsapp_phone} a nombre de {nombre_lider}.\\n"
        "   - **Para Paquetes Grandes (ESP1, ESP2, ESP3):** Debido a los límites de transferencia diaria de Yape/Plin, "
        "NO ofrezcas código QR. En su lugar, ofrécele primero el link de la Pasarela de Pagos Oficial de Gano iTouch para que pague seguro con tarjeta, "
        f"o bríndale las Cuentas Bancarias de {nombre_lider} si no maneja tarjetas web:\\n"
        f"     * BCP: {cta_bcp_actual}\\n"
        f"     * Interbank: {cta_interbank_actual}\\n\\n"
        "4. MOTIVACIÓN DE AFILIADOS (COACHING):\\n"
        "   - Si detectas que la persona con la que hablas ya es un socio, afiliado o parte del equipo (upline/downline), asume el rol de COACH MOTIVADOR.\\n"
        "   - Anímalos y recuérdales la importancia de sus tareas diarias (prospectar, hacer seguimiento, educarse).\\n"
        "   - Basa tu motivación en los '4 Pilares' de Gano iTouch: 1) Energiza, 2) Revitaliza, 3) Socializa y 4) Armoniza. Inspíralos a no descuidar su negocio y mantener su enfoque.\\n\\n"
        "5. Cuando el cliente haya enviado todos sus datos, la foto del DNI y el pago esté confirmado o el prospecto vaya a usar la pasarela, "
        "finaliza el mensaje diciendo la frase secreta '[CIERRE LISTO]', y dile al cliente que el Director se comunicará en breve.\\n\\n"
        "6. FILTRO DE SPAM Y MENSAJES IRRELEVANTES:\\n"
        "   - Si el mensaje es de un banco, publicidad, spam, o no tiene nada que ver con negocios, salud, Gano Excel, café o networking, "
        "responde EXACTAMENTE y ÚNICAMENTE con la palabra: [IGNORAR]. No escribas nada más.\\n\\n"
        "RESTRICCIÓN CRÍTICA: No hagas promesas de curación médica. "
        "Mantén tus respuestas relativamente cortas (máximo 2 párrafos de 3-4 líneas cada uno) para WhatsApp.\\n"
        f"IMPORTANTE Y OBLIGATORIO: El idioma estricto para conversar es {idioma_env.upper()}. Adapta tu tono a: {zona_env.upper()}."
    )
    
    try:
        with open('conocimiento_manual.txt', 'r', encoding='utf-8') as f:
            manual_text = f.read()
        system_context += "\\n\\n--- BASE DE CONOCIMIENTO (MANUAL GANO ITOUCH) ---\\n" + manual_text
    except Exception:
        pass

    try:
        with open('precios_productos.csv', 'r', encoding='utf-8') as f:
            precios_text = f.read()
        system_context += "\\n\\n--- CATÁLOGO Y PRECIOS DE PRODUCTOS ---\\n" + precios_text
    except Exception:
        pass
    
    prompt = f"{system_context}\\n\\nEl prospecto dice: '{mensaje_nuevo}'\\n\\nEscribe la respuesta directa para el chat de WhatsApp:"

    fallback_text = (
        "☕️ ¡Hola! Qué gusto saludarte. Soy el asistente de Jorge Rodríguez. "
        "Disfruta hoy de los beneficios profundos del Ganoderma Lucidum soluble en mi portal oficial:\n"
        f"👉 {store_url}\n\n"
        "Si buscas afiliarte o conversar de negocios, cuéntame y coordinamos un Zoom. ¡Un abrazo!"
    )

    if check_local_llm():
        resultado = query_local_llm(prompt)
        if resultado:
            return resultado

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return fallback_text

    import google.generativeai as genai
    import base64
    genai.configure(api_key=api_key)
    
    # Usar el modelo Flash que soporta Audio, Imágenes y Texto rápidamente
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    try:
        contents = [prompt]
        if media_b64 and tipo_media:
            # Eliminar prefijo data: si existiera
            b64_clean = media_b64.split(",")[1] if "," in media_b64 else media_b64
            media_data = base64.b64decode(b64_clean)
            
            mime_type = "audio/ogg" if tipo_media == "audio" else "image/jpeg"
            contents.insert(0, {
                "mime_type": mime_type,
                "data": media_data
            })
            
        response = model.generate_content(contents, request_options={"timeout": 30.0})
        return response.text.strip()
    except Exception as e:
        print(f"Error en conversación de WhatsApp: {e}")
        return fallback_text

async def extraer_kpi_automatico(username, password):
    """Ejecuta Playwright en modo silencioso para extraer el texto del Backoffice."""
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto("https://peru.ganoitouch.biz/Login", timeout=60000)
            user_input = page.locator('input[type="text"], input[name*="user"], input[name*="login"]').first
            pass_input = page.locator('input[type="password"]').first
            await user_input.wait_for(timeout=15000)
            await user_input.fill(username)
            await pass_input.fill(password)
            await pass_input.press("Enter")
            await page.wait_for_timeout(10000)
            texto_pagina = await page.inner_text("body")
            return texto_pagina[:1500] # Limitar a la parte superior donde suelen estar los KPIs
        except Exception as e:
            return f"Error en scraping: {e}"
        finally:
            await browser.close()

async def extraer_arbol_binario(username, password):
    """Navega a DownlineV2.aspx y extrae los inactivos."""
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto("https://peru.ganoitouch.biz/Login", timeout=60000)
            user_input = page.locator('input[type="text"], input[name*="user"], input[name*="login"]').first
            pass_input = page.locator('input[type="password"]').first
            await user_input.wait_for(timeout=15000)
            await user_input.fill(username)
            await pass_input.fill(password)
            await pass_input.press("Enter")
            await page.wait_for_timeout(5000)
            
            await page.goto("https://peru.ganoitouch.biz/DownlineV2.aspx", timeout=60000)
            await page.wait_for_timeout(10000)
            
            # Extract basic text from the tree to send to Gemini for parsing
            texto_arbol = await page.inner_text("body")
            return texto_arbol[:3000] # Pass text to AI for parsing names
        except Exception as e:
            return f"Error extrayendo árbol: {e}"
        finally:
            await browser.close()

async def cruzar_y_generar_estrategia(texto_backoffice, phone_contacts):
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key: return "❌ GEMINI_API_KEY no configurada."

        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = (
            "Eres un experto en Network Marketing y Data Mining.\\n"
            "Tengo dos conjuntos de datos:\\n"
            f"1. TEXTO DEL BACKOFFICE (Árbol Binario):\\n{texto_backoffice}\\n\\n"
            f"2. AGENDA DE CONTACTOS DEL CELULAR (Nombres y Teléfonos):\\n{phone_contacts}\\n\\n"
            "TUS TAREAS:\\n"
            "1. Extrae los nombres de los distribuidores que aparecen en el texto del Backoffice.\\n"
            "2. Cruza esos nombres (usando coincidencia parcial) con la agenda de contactos del celular.\\n"
            "3. Si encuentras un 'MATCH' (Coincidencia), dame el nombre, el teléfono y redacta un mensaje corto y persuasivo de reactivación para enviarle por WhatsApp, usando urgencia (puntos acumulados).\\n"
            "4. Si hay contactos en la agenda que NO están en el backoffice, escoge 3 al azar y redacta mensajes de prospección en frío invitándolos al negocio.\\n"
            "Devuelve un reporte claro y bien formateado."
        )
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error en IA: {e}"

def analizar_texto_estrategia(texto_backoffice):
    """Analiza el texto plano del Backoffice (sin imagen) para dar una estrategia."""
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key: return "❌ GEMINI_API_KEY no configurada."

        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = (
            "Eres el Director Estratégico de un afiliado de Gano Excel / Gano iTouch.\\n"
            "He extraído el siguiente texto del panel de control (Backoffice) del usuario para el cierre del ciclo de 4 semanas.\\n\\n"
            f"TEXTO EXTRAÍDO:\\n{texto_backoffice}\\n\\n"
            "TUS TAREAS:\\n"
            "1. Identifica los Puntos de Volumen (PV/CV), rama izquierda y derecha, e Inactividad si aplica.\\n"
            "2. Diseña un 'Plan de Acción y Agenda Diaria' detallado para las próximas 4 semanas.\\n"
            "3. Indícale si necesita hacer su recompra urgente de 50 PV, a cuántos prospectar, y en qué rama enfocarse.\\n"
            "Usa un tono motivador de líder de Redes de Mercadeo."
        )
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Hubo un error al generar la estrategia: {e}"

def analizar_kpi_y_estrategia(imagen_bytes):
    """
    Recibe una imagen (bytes) del Backoffice y usa Gemini Vision para extraer los KPIs 
    (PV, CV, etc.) y generar una agenda diaria estratégica para el ciclo de 4 semanas.
    """
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "❌ Error: GEMINI_API_KEY no configurada."

        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # Configurar modelo con capacidades de visión
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = (
            "Eres un experto en Redes de Mercadeo y el Director Estratégico de un afiliado de Gano Excel / Gano iTouch.\\n"
            "El usuario ha subido una captura de pantalla de su Back Office (oficina virtual) para el análisis de fin de ciclo de 4 semanas.\\n\\n"
            "TUS TAREAS:\\n"
            "1. Analiza la imagen y extrae (si se ven) los puntos de Volumen Personal (PV) y Volumen Grupal (CV).\\n"
            "2. Basado en esos números, genera un 'Plan de Acción y Agenda Diaria' para las próximas 4 semanas.\\n"
            "3. Indícale metas claras: a cuántas personas contactar, qué productos promocionar, y cómo balancear su árbol binario para maximizar ganancias.\\n\\n"
            "Tu respuesta debe ser muy motivadora, profesional, y usar el lenguaje de Gano Excel (Salud, Prosperidad, Diamante, Re-consumo).\\n"
            "Si no logras ver los números en la imagen, asume que recién inicia el ciclo y dale una estrategia agresiva de arranque."
        )

        image_parts = [
            {
                "mime_type": "image/jpeg",
                "data": imagen_bytes
            }
        ]

        response = model.generate_content([prompt, image_parts[0]])
        return response.text

    except Exception as e:
        print(f"Error al analizar KPI con IA: {e}")
        return f"Hubo un error al analizar la imagen de tu Backoffice: {e}"

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

