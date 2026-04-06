# DOCUMENTACIÓN MAESTRA: Sinergia Gano Bot v3.0

Esta documentación certifica la estructura y el poder detrás de uno de los ecosistemas de automatización de Inbound Marketing más robustos de la industria del Network Marketing (Gano Excel / Gano iTouch).

## La Maquinaria Central (Modelo 1 - Local Descentralizado)

El software reside en `C:\GanoiTouch` y está segmentado en 5 Módulos o "Fases" que actúan como un embudo perfecto: atracción, posteo masivo y cierre.

### Fase 1 y 2: El Escuadrón de Vuelo Inmune (publisher.py)
*   **Qué hace:** Utiliza `Playwright` en modo de contexto persistente para abrir Facebook burlando la Autenticación de Dos Pasos (2FA) y el algoritmo anti-bot. 
*   **Alcance Semántico:** Navega sigilosamente a tu página "Gano Excel", arroja posteos con un gestor multimedia asombroso que no repite imágenes. Luego, ataca grupos enteros georreferenciados (ej. 'Mercado de la Molina') en lapsos de 30-90 segundos para emular la latencia y paciencia humana.

### Fase 3: Ecosistema Descentralizado e Instalación Inteligente
*   **Qué hace:** Hemos transformado a esto en una franquicia digital distribuible. Con el script interactivo `Configurar_Tu_Bot.bat` / `setup.py`, tus downlines solo hacen doble clic y el bot los lleva de la mano configurando sus variables de entorno `.env` (Página de Facebook y URL GanoiTouch) sin que entiendan de programación.

### Fase 4: La Fábrica Autónoma (auto_creator.py)
*   **Qué hace:** Evita que el afiliado use Canva o herramientas externas de alto costo. Invocando al script de gráficos interno `Pillow`, fabrica imágenes 1080x1080 con 14 variedades de "Llamados a la Acción" ("Hooks") aprobados éticamente sobre *Refuerzos de Salud Integral* e *Ingresos Residuales*. El material se inyecta en `/imagenes/negocio` y `/imagenes/salud` para nutrir la rotación semanal.

### Fase 5: La Secretaria Virtual o Sales Bot (whatsapp_bot.py)
*   **Qué hace:** El embudo táctico de fondo de olla. Usando igualmente el contexto indetectable de `Playwright` asíncrono sobre `web.whatsapp.com`, "La Vigilante" detecta usuarios entrantes atraídos por la red social. Les ofrece los 5 botones mágicos ("Productos", "Negocio", "Cita", "Dudas Salud", "Dudas Red").
*   **El Gran Remate:** Liquida cualquier duda explicando que Gano Excel no es magia sino nutrición celular. Dirige al "prospecto asustado" explicándole exactamente donde hundir de la web para crearse una cuenta segura y recoger en "Sede de Av Angamos Oeste", quitándole al patrocinador (tú) el estrés de lidiar transaccionalmente con el flujo del dinero.
