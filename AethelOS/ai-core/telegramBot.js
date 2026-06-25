require('dotenv').config();
const TelegramBot = require('node-telegram-bot-api');
const { processMessage } = require('./agentBrain');
const { executeWhatsAppSend } = require('./tools');
const { supabase } = require('./db');
const path = require('path');

const token = process.env.TELEGRAM_BOT_TOKEN;

if (!token || token === "tu_token_aqui") {
  console.error("Falta configurar TELEGRAM_BOT_TOKEN en el .env");
  process.exit(1);
}

// Crear el bot con polling
const bot = new TelegramBot(token, { polling: true });

console.log("🤖 Servicio de Telegram Iniciado y escuchando mensajes...");

// Guardar la sesión de con qué agente está hablando cada usuario
const userSessions = {};

// Guardar el historial de mensajes
const chatHistories = {};

// Estado para rastrear si el usuario está modificando un borrador (HITL)
const pendingModifications = {};
// Estado para almacenar el último borrador generado por usuario
const pendingDrafts = {};

// Escuchar mensajes entrantes
bot.on('message', async (msg) => {
  const chatId = msg.chat.id;
  let userText = msg.text || msg.caption || "";
  const userName = msg.from.first_name;

  let imageUrl = null;
  let isVoice = false;

  try {
    // 1. Manejar Fotos (Visión)
    if (msg.photo && msg.photo.length > 0) {
      const photoId = msg.photo[msg.photo.length - 1].file_id; // Mayor resolución
      imageUrl = await bot.getFileLink(photoId);
      userText = userText + "\n[El usuario ha enviado una imagen adjunta]";
    }

    // 2. Manejar Documentos (PDF)
    if (msg.document) {
      const docId = msg.document.file_id;
      const docName = msg.document.file_name;
      const mimeType = msg.document.mime_type;
      const fileSize = msg.document.file_size;

      if (mimeType === 'application/pdf') {
        if (fileSize > 10 * 1024 * 1024) { // Límite de 10MB
          return bot.sendMessage(chatId, "⚠️ El documento excede el límite de 10MB. Por favor, recorta el PDF para no saturar mi memoria.");
        }
        
        bot.sendChatAction(chatId, 'upload_document');
        bot.sendMessage(chatId, `Analizando documento: ${docName}...`);
        
        const fileUrl = await bot.getFileLink(docId);
        const response = await require('axios').get(fileUrl, { responseType: 'arraybuffer' });
        const pdfParse = require('pdf-parse');
        const pdfData = await pdfParse(response.data);
        
        let documentText = pdfData.text;
        userText = userText + `\n[Contenido del PDF adjunto '${docName}']:\n` + documentText.substring(0, 20000); // Límite de ~20k caracteres
        
        if (pdfData.numpages > 15) {
          bot.sendMessage(chatId, `⚠️ Aviso: El documento tiene ${pdfData.numpages} páginas. Solo he memorizado el contenido inicial para mantener mi agilidad cognitiva.`);
        }
      } else if (mimeType && mimeType.startsWith('image/')) {
        // Manejar imágenes enviadas como "Archivo" en lugar de "Foto"
        bot.sendChatAction(chatId, 'upload_photo');
        imageUrl = await bot.getFileLink(docId);
        userText = userText + "\n[El usuario ha enviado una imagen como archivo adjunto]";
      } else {
        return bot.sendMessage(chatId, `Aún no puedo leer archivos del tipo ${mimeType}. Por favor envíame PDFs o Imágenes.`);
      }
    }

    // 3. Manejar Notas de Voz (Audio In)
    if (msg.voice) {
      bot.sendChatAction(chatId, 'record_voice');
      bot.sendMessage(chatId, "Escuchando tu nota de voz...");
      
      const fileUrl = await bot.getFileLink(msg.voice.file_id);
      const response = await require('axios').get(fileUrl, { responseType: 'arraybuffer' });
      
      const tempPath = path.join(__dirname, `temp_voice_${Date.now()}.ogg`);
      require('fs').writeFileSync(tempPath, response.data);
      
      const { OpenAI } = require('openai');
      const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY, baseURL: 'https://api.groq.com/openai/v1' });
      
      const transcription = await openai.audio.transcriptions.create({
        file: require('fs').createReadStream(tempPath),
        model: "whisper-large-v3",
      });
      
      userText = transcription.text;
      require('fs').unlinkSync(tempPath);
      isVoice = true;
      bot.sendMessage(chatId, `🗣️ *Has dicho:* "${userText}"`, { parse_mode: "Markdown" });
    }

  } catch (error) {
    console.error("Error procesando adjuntos:", error);
    return bot.sendMessage(chatId, "Hubo un problema procesando tu archivo o nota de voz.");
  }

  if (!userText && !imageUrl) return; 

  console.log(`[Telegram] Mensaje de ${userName}: ${userText}`);
  
  if (!chatHistories[chatId]) {
    chatHistories[chatId] = [];
  }

  // Cargar lista dinámica de agentes desde JSON
  const personasPath = path.join(__dirname, 'local_db', 'agent_personas.json');
  let personas = {};
  try {
    personas = JSON.parse(require('fs').readFileSync(personasPath, 'utf-8'));
  } catch(e) {}
  
  const textLower = typeof userText === 'string' ? userText.toLowerCase() : "";

  // Comandos para cambiar de agente dinámicamente
  if (textLower.startsWith('/conectar ')) {
    const target = userText.substring(10).trim();
    if (personas[target]) {
      userSessions[chatId] = target;
      return bot.sendMessage(chatId, `🔌 *Conexión establecida con ${target}*.\nEnlace directo completado. ¿En qué te ayudo?`, { parse_mode: "Markdown" });
    } else {
      return bot.sendMessage(chatId, `❌ Agente '${target}' no encontrado en los registros corporativos.`);
    }
  }

  // Comandos legacy (atajos)
  if (textLower === '/contrato') {
    const contractPath = path.join(__dirname, '..', '..', 'brain', '9eb4ec31-d5ce-4bc5-a7d0-c09eb14cbb2d', 'Propuesta_Agente_QIS.md');
    try {
      await bot.sendDocument(chatId, contractPath, { caption: "📄 Aquí tienes el borrador del contrato para QIS SAC." });
      return;
    } catch(e) {
      return bot.sendMessage(chatId, "No pude encontrar el archivo del contrato.");
    }
  }

  if (textLower === '/paul' || textLower === '/nexus') {
    userSessions[chatId] = "Nexus_Alpha";
    return bot.sendMessage(chatId, "🔌 *Conexión establecida con Nexus_Alpha (Paul)*.\nEstratega listo.", { parse_mode: "Markdown" });
  }

  if (textLower === '/travis') {
    userSessions[chatId] = "Travis";
    return bot.sendMessage(chatId, "🔌 *Conexión establecida con Travis* (Tactical Resource Acquisition & Validation Intelligent System).\nListo para cotizar.", { parse_mode: "Markdown" });
  }
  if (textLower === '/sophia' || textLower === '/cipher') {
    userSessions[chatId] = "Cipher_Protocol";
    return bot.sendMessage(chatId, "🔌 *Conexión establecida con Cipher_Protocol (Sophia)*.\nMarketing listo.", { parse_mode: "Markdown" });
  }

  // Agente por defecto si no ha seleccionado uno
  const agentName = userSessions[chatId] || "Nexus_Alpha";
  // El ID del agente ahora necesita resolverse dinámicamente desde Supabase, pero por ahora enrutaremos con ID dummy si es nuevo
  const agentId = agentName === "Nexus_Alpha" ? "A-001" : (agentName === "Cipher_Protocol" ? "A-002" : `A-${Math.floor(Math.random()*900)+100}`);

  // Enviar un mensaje de "escribiendo..." mientras el agente piensa
  bot.sendChatAction(chatId, 'typing');

  try {
    // Si estábamos en modo modificación, agregamos el contexto al mensaje
    if (pendingModifications[chatId]) {
      userText = `[FEEDBACK HITL - MODIFICACIÓN REQUERIDA]: Corrige tu borrador anterior aplicando este feedback del humano: "${userText}"`;
      delete pendingModifications[chatId];
    }

    // Pasar el historial de mensajes, ahora aceptando imageUrl e isVoice
    const result = await processMessage(agentName, chatHistories[chatId], userText, imageUrl);
    
    // Guardar el mensaje del usuario y la respuesta en el historial para contexto futuro
    // Si hubo imagen, no guardamos el objeto complejo en el historial de chatHistories, solo texto, para no romper futuros turnos.
    chatHistories[chatId].push({ role: "user", content: userText });
    chatHistories[chatId].push({ role: "assistant", content: result.reply });
    
    // Mantener el historial manejable (máximo últimos 10 mensajes)
    if (chatHistories[chatId].length > 10) {
      chatHistories[chatId] = chatHistories[chatId].slice(-10);
    }

    // Enviar respuesta base por Telegram
    bot.sendMessage(chatId, result.reply);
    
    // Si el usuario envió una nota de voz, respondemos también con nota de voz usando google-tts-api
    if (isVoice) {
      try {
        const googleTTS = require('google-tts-api');
        // Cortar la respuesta a 200 caracteres para el TTS gratuito o dividirla en partes
        const textForVoice = result.reply.length > 200 ? result.reply.substring(0, 200) + "..." : result.reply;
        const audioUrl = googleTTS.getAudioUrl(textForVoice, {
          lang: 'es',
          slow: false,
          host: 'https://translate.google.com',
        });
        await bot.sendVoice(chatId, audioUrl);
      } catch (e) {
        console.error("Error generando nota de voz TTS:", e);
      }
    }
    
    // Actualizar estado en Supabase para el Frontend 3D
    await supabase.from('aethel_agents').update({
      operational_status: 'active',
      current_action: `Procesando acción para ${userName}`,
      agent_thought: result.reply.substring(0, 50) + "..."
    }).eq('agent_id', agentId);
    
    // Si el agente decidió transferir la conversación
    if (result.type === 'transfer') {
      userSessions[chatId] = result.transferTo;
      const targetName = result.transferTo === "Nexus_Alpha" ? "Paul" : "Sophia";
      setTimeout(() => {
        bot.sendMessage(chatId, `🔌 *Conexión transferida a ${result.transferTo} (${targetName})*`, { parse_mode: "Markdown" });
      }, 1000);
    }
    
    // Si el agente preparó un correo, pedir aprobación
    if (result.type === 'draft_email') {
      const email = result.emailData;
      const approvalMessage = `📧 *BORRADOR DE CORREO (Esperando aprobación)*\n\n*Para:* ${email.destinatario}\n*Asunto:* ${email.asunto}\n\n*Cuerpo:*\n${email.cuerpo}`;
      
      const opts = {
        parse_mode: "Markdown",
        reply_markup: {
          inline_keyboard: [
            [
              { text: "✅ Aprobar", callback_data: "approve_draft" },
              { text: "📝 Modificar", callback_data: "modify_draft" },
              { text: "❌ Rechazar", callback_data: "reject_draft" }
            ]
          ]
        }
      };
      
      setTimeout(() => { bot.sendMessage(chatId, approvalMessage, opts); }, 1500);
    }
    
    // Si el agente preparó un WhatsApp
    if (result.type === 'draft_whatsapp') {
      const wa = result.draftData;
      pendingDrafts[chatId] = { type: 'whatsapp', data: wa };
      
      const approvalMessage = `📱 *BORRADOR DE WHATSAPP (HITL)*\n\n*Para:* ${wa.target_name}\n*Teléfono:* ${wa.target_phone}\n\n*Mensaje:*\n${wa.message_body}`;
      
      const opts = {
        parse_mode: "Markdown",
        reply_markup: {
          inline_keyboard: [
            [
              { text: "✅ Aprobar y Enviar", callback_data: "approve_draft" },
              { text: "📝 Modificar", callback_data: "modify_draft" },
              { text: "❌ Rechazar", callback_data: "reject_draft" }
            ]
          ]
        }
      };
      setTimeout(() => { bot.sendMessage(chatId, approvalMessage, opts); }, 1500);
    }
    
    // Si el agente preparó una Cotización / Tabla
    if (result.type === 'draft_quote') {
      const q = result.draftData;
      const approvalMessage = `📊 *BORRADOR DE COTIZACIÓN (HITL)*\n\n*Proveedor:* ${q.provider}\n*Costo Total:* ${q.total_cost}\n*Margen:* ${q.profit_margin}\n\n*Ítems:*\n${q.items}`;
      
      const opts = {
        parse_mode: "Markdown",
        reply_markup: {
          inline_keyboard: [
            [
              { text: "✅ Aprobar", callback_data: "approve_draft" },
              { text: "📝 Modificar", callback_data: "modify_draft" },
              { text: "❌ Rechazar", callback_data: "reject_draft" }
            ]
          ]
        }
      };
      setTimeout(() => { bot.sendMessage(chatId, approvalMessage, opts); }, 1500);
    }

  } catch (error) {
    console.error("Error al responder en Telegram:", error);
    bot.sendMessage(chatId, "Lo siento, tuve un problema interno de conexión con mis sistemas centrales.");
  }
});

// Manejar los clics en los botones de aprobación
bot.on('callback_query', async (query) => {
  const chatId = query.message.chat.id;
  const action = query.data;
  
  if (action === 'approve_draft' || action === 'approve_email') {
    bot.editMessageReplyMarkup({ inline_keyboard: [] }, { chat_id: chatId, message_id: query.message.message_id });
    
    // Verificamos si hay un draft pendiente de WhatsApp para este chat
    const draft = pendingDrafts[chatId];
    if (draft && draft.type === 'whatsapp') {
      bot.sendMessage(chatId, "⏳ *Enviando mensaje a la API de WhatsApp Cloud...*", { parse_mode: "Markdown" });
      try {
        await executeWhatsAppSend(draft.data.target_phone, draft.data.message_body);
        bot.sendMessage(chatId, "✅ *¡Mensaje enviado con éxito vía WhatsApp API oficial!*", { parse_mode: "Markdown" });
      } catch (err) {
        bot.sendMessage(chatId, `❌ *Error al enviar WhatsApp:* ${err.message}\nVerifica que los Tokens de Meta estén en el archivo .env`, { parse_mode: "Markdown" });
      }
      delete pendingDrafts[chatId];
    } else {
      bot.sendMessage(chatId, "✅ *Borrador Aprobado y Guardado.* Acción confirmada.", { parse_mode: "Markdown" });
    }
    
  } else if (action === 'reject_draft' || action === 'reject_email') {
    bot.editMessageReplyMarkup({ inline_keyboard: [] }, { chat_id: chatId, message_id: query.message.message_id });
    bot.sendMessage(chatId, "❌ *Borrador Rechazado.* Operación abortada.", { parse_mode: "Markdown" });
    delete pendingDrafts[chatId];
  } else if (action === 'modify_draft') {
    bot.editMessageReplyMarkup({ inline_keyboard: [] }, { chat_id: chatId, message_id: query.message.message_id });
    pendingModifications[chatId] = true;
    bot.sendMessage(chatId, "📝 *Modo Edición Activado.*\nPor favor, envíame una nota de voz o escribe qué correcciones deseas que le haga al borrador.", { parse_mode: "Markdown" });
  }
});
