# Sinergia Bot (Multi-Tenant AI) 🚀☕

Sinergia Bot es un ecosistema avanzado de automatización, ventas y prospección multinivel diseñado específicamente para **Gano iTouch (Excel)**. Desarrollado y administrado por el líder Jorge Rodríguez, este proyecto combina Inteligencia Artificial, automatización de WhatsApp y una aplicación móvil para transformar la manera en que los afiliados interactúan con sus prospectos.

## 🌟 Características Principales

### 1. Bot de WhatsApp (Playwright + IA)
- **Modo Vigía:** Escanea la versión web de WhatsApp buscando chats "no leídos".
- **Respuesta Inteligente:** Lee los mensajes y genera respuestas conversacionales automáticas usando Google Gemini 1.5 Flash.
- **Notas de Voz Realistas (TTS):** Genera y envía notas de voz hiperrealistas simulando ser un asistente humano utilizando Microsoft Edge-TTS (voces neuronales como Jorge o Gonzalo).
- **Control de Contexto:** El bot tiene inyectado el Manual de Gano iTouch y el Catálogo de Precios Oficial (Pioir Coffee, ESP1, ESP2, ESP3). Conoce exactamente el CV, PV y las reglas del bono binario.
- **Intervención Manual (Hand-off):** Desde la app móvil, el afiliado puede darle una orden al bot para que busque un contacto específico y retome la charla, pasándole el contexto deseado a la Inteligencia Artificial.

### 2. Ecosistema Multi-Tenant (API + SQLite)
- Múltiples afiliados pueden registrarse y tener su propio "orquestador" de WhatsApp.
- Base de datos centralizada (`sinergia_cloud.db`) que guarda la configuración de cada líder, cuentas bancarias, Yape/Plin y enlaces a sus tiendas virtuales.
- Despliegue en VPS Linux (Ubuntu) ejecutando instancias de Chromium sin cabeza.

### 3. Sinergia Mobile (App para Afiliados)
- App construida con **Vite + Vanilla JS + Capacitor** para Android y Web.
- **Dashboard de Control:** Monitoreo de estado de WhatsApp y enlace con Fanpages de Facebook.
- **Simulador Servilleta:** Calculadora interactiva y exacta de proyecciones financieras para paquetes ESP, consumo base y rangos (Plata, Oro, Diamante).
- **Módulo de Cobros:** Sube tu código QR de Yape y Plin. El bot enviará automáticamente tu imagen cuando un prospecto diga la palabra mágica.
- **Bot Control:** Interfaz visual para enviar órdenes remotas al Bot de IA para que retome la conversación con un cliente indeciso.
- **Reclutamiento Auto-Post:** Generación de copies optimizados usando IA para publicar en tu página de Facebook automáticamente.

## 🛠 Instalación y Configuración

El orquestador en la nube (`deploy_vps.py`) se encarga de empaquetar el código, enviarlo al VPS y ejecutar el script `restart_ninja.sh` que instala las dependencias de Python y levanta el servidor web (`api_mobile.py`) y el orquestador (`whatsapp_bot.py`) en paralelo.

### Requisitos Locales (Para la App Móvil):
1. Node.js y npm
2. Android Studio (para compilar la APK nativa)
3. Ejecutar: `npm run build` seguido de `npx cap sync android` y compilar en Android Studio o Gradle.
