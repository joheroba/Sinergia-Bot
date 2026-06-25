import os
import requests
import time

# === CONFIGURACION DE MOTOR DE VOZ ===
MOTOR_ACTUAL = "COLAB_LOCAL" # Opciones: "ELEVENLABS", "COLAB_LOCAL"

# === CONFIGURACION ELEVENLABS ===
API_KEY = "sk_d046ea34c2103bfd746c9ffd3920b54a1a74e39b454ebb8d"
VOICE_ID = "hKNojvfa5tHXCmTgw99A" # Voz de Patricia
URL_ELEVENLABS = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

# === CONFIGURACION COLAB / OMNIVOICE (XTTS) ===
URL_COLAB = "https://flammable-handwash-backstage.ngrok-free.dev/api/tts"
COLAB_VOICE_MODEL = "aris_sample.mp3" # Nombre de tu archivo MP3 de 3 a 6 segundos

BASE_DIR = r"C:\Users\Usuario1\.gemini\antigravity\scratch\AethelOS\ventas"

def generar_nota_voz(texto_a_sintetizar, nombre_archivo):
    ruta_salida = os.path.join(BASE_DIR, nombre_archivo)
    
    if MOTOR_ACTUAL == "ELEVENLABS":
        print(f"\n[SISTEMA TTS - ELEVENLABS] Grabando nota de voz con ElevenLabs...")
        print(f"Texto: '{texto_a_sintetizar}'")
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": API_KEY
        }
        data = {
            "text": texto_a_sintetizar,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
        }
        try:
            response = requests.post(URL_ELEVENLABS, json=data, headers=headers)
            if response.status_code == 200:
                with open(ruta_salida, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk: f.write(chunk)
                print(f"[SISTEMA TTS] EXITO: -> {ruta_salida}")
                return ruta_salida
            else:
                print(f"[SISTEMA TTS] ERROR {response.status_code}: {response.text}")
        except Exception as e:
            print(f"[SISTEMA TTS] ERROR: {str(e)}")

    elif MOTOR_ACTUAL == "COLAB_LOCAL":
        print(f"\n[SISTEMA TTS - ARIS/COLAB] Conectando con servidor local/Colab para sintetizar voz...")
        print(f"Texto: '{texto_a_sintetizar}'")
        
        # Simulación de payload para RVC / XTTS / OmniVoice
        payload = {
            "text": texto_a_sintetizar,
            "model": COLAB_VOICE_MODEL,
            "language": "es"
        }
        
        try:
            # Peticion real al servidor de XTTS en Colab
            print(f"[SISTEMA TTS] Petición POST enviada a {URL_COLAB} usando modelo {COLAB_VOICE_MODEL}")
            response = requests.post(URL_COLAB, json=payload)
            
            if response.status_code == 200:
                # Escribimos el binario mp3 devuelto por la IA
                with open(ruta_salida, 'wb') as f:
                    f.write(response.content)
                print(f"[SISTEMA TTS] EXITO: Audio clonado generado con la voz de Aris -> {ruta_salida}")
                return ruta_salida
            else:
                print(f"[SISTEMA TTS] ERROR DEL SERVIDOR {response.status_code}: {response.text}")
            return ruta_salida
            
        except requests.exceptions.ConnectionError:
            print(f"[SISTEMA TTS] ERROR: No se pudo conectar al servidor de Colab en {URL_COLAB}. ¿Está encendido?")
            
    return None

# === MAQUINA DE ESTADOS (EMBUDO EN FRIO) ===
def ejecutar_embudo_ventas():
    print("==================================================")
    print(" INICIANDO EMBUDO DE VENTAS GANOIBOT (MERCADO FRIO) ")
    print("==================================================\n")
    
    print(">> [Evento] Entra un nuevo mensaje a WhatsApp desde una campana de FB Ads.")
    prospecto_mensaje_1 = "Hola, vi su anuncio del cafe saludable y me gustaria mas informacion."
    print(f"Prospecto (WhatsApp): \"{prospecto_mensaje_1}\"")
    time.sleep(1)
    
    # FASE 1: Filtro de Texto (Formalidad)
    print("\n--- FASE 1: FILTRO Y CAPTURA DE DATOS (TEXTO) ---")
    texto_respuesta_1 = "¡Hola! Que gusto saludarte. Soy el asistente virtual de Sinergia Pro. Para brindarte la informacion correcta, ¿me podrias confirmar tu nombre y de que ciudad nos escribes?"
    print(f"GanoiBot (WhatsApp Texto): \"{texto_respuesta_1}\"")
    time.sleep(2)
    
    prospecto_mensaje_2 = "Soy Juan Carlos, desde Lima, Peru."
    print(f"\nProspecto (WhatsApp): \"{prospecto_mensaje_2}\"")
    time.sleep(1)
    
    # FASE 2: Hibrido (Voz) - Cualificacion y Empatia
    print("\n--- FASE 2: EMPATIA Y CUALIFICACION (VOZ SINTETIZADA) ---")
    print(">> [Sistema] El bot determina que es seguro enviar audio porque ya recabo los datos duros.")
    
    texto_audio_2 = "¡Excelente Juan Carlos, un gusto saludarte hasta Lima! Te cuento rápidamente, nuestro proyecto con Sinergia Pro no solo se trata del café más saludable enriquecido con Ganoderma, sino de un modelo de negocio que te permite generar ingresos residuales. Cuéntame con total confianza, ¿te interesa más consumir el producto para mejorar tu salud o estás buscando una forma inteligente de diversificar tus ingresos?"
    generar_nota_voz(texto_audio_2, "calificacion_juan_carlos.mp3")
    
    time.sleep(2)
    
    prospecto_mensaje_3 = "La verdad me interesan ambas, pero mas que nada el negocio porque estoy buscando ingresos extra."
    print(f"\nProspecto (WhatsApp Voice Note): \"{prospecto_mensaje_3}\"")
    time.sleep(1)

    # FASE 3: Cierre Automatizado
    print("\n--- FASE 3: CIERRE AUTOMATIZADO ---")
    print(">> [Sistema] La temperatura del lead sube a: CALIENTE. Ejecutando cierre.")
    
    texto_audio_3 = "Esa es la mentalidad que buscamos, Juan Carlos. Entrar al negocio con nosotros significa que vas a tener el mejor producto y la mejor tecnología trabajando para ti. Te estoy enviando aquí abajo en texto mi enlace oficial para que adquieras tu paquete PIOIR y tu código quede activado hoy mismo. ¡Cualquier duda en el registro, aquí estoy para guiarte!"
    generar_nota_voz(texto_audio_3, "cierre_juan_carlos.mp3")
    
    texto_cierre = "Aquí tienes el enlace seguro para registrarte en Gano iTouch: https://peru.ganoexcel.com/SinergiaProTest\n¡Avisame cuando completes el paso 1!"
    print(f"\nGanoiBot (WhatsApp Texto): \"{texto_cierre}\"")

    print("\n==================================================")
    print(" EMBUDO COMPLETADO. AFILIACION EN PROCESO.")
    print("==================================================")

if __name__ == "__main__":
    ejecutar_embudo_ventas()
