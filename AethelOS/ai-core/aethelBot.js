require('dotenv').config();
const TelegramBot = require('node-telegram-bot-api');
const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');

const token = process.env.AETHEL_BOT_TOKEN;
const bot = new TelegramBot(token, { polling: true });

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

console.log("🌐 Meta-Bot AethelOS Iniciado y escuchando comandos...");

bot.onText(/\/start/, (msg) => {
  bot.sendMessage(msg.chat.id, "🤖 *Bienvenido a AethelOS Admin*\nSoy el controlador del Metaverso Corporativo.\n\nComandos:\n/clonar [Nombre] | [Directiva] - Crea un nuevo agente.\n/agentes - Lista los agentes activos en la corporación.", { parse_mode: 'Markdown' });
});

bot.onText(/\/agentes/, (msg) => {
  const personasPath = path.join(__dirname, 'local_db', 'agent_personas.json');
  let personas = {};
  if (fs.existsSync(personasPath)) {
    personas = JSON.parse(fs.readFileSync(personasPath, 'utf-8'));
  }
  
  let lista = "📊 *AGENTES ACTIVOS EN AETHEL_OS:*\n\n";
  for (const [name, directive] of Object.entries(personas)) {
    lista += `👤 *${name}*\n_${directive.substring(0, 50)}..._\n\n`;
  }
  
  bot.sendMessage(msg.chat.id, lista, { parse_mode: 'Markdown' });
});

bot.onText(/\/clonar (.+)/, async (msg, match) => {
  const chatId = msg.chat.id;
  const params = match[1].split('|');
  
  if (params.length < 2) {
    return bot.sendMessage(chatId, "⚠️ Formato incorrecto. Uso:\n`/clonar Nombre | Directiva del agente`", { parse_mode: 'Markdown' });
  }
  
  const name = params[0].trim();
  const directive = params[1].trim();
  const newAgentId = `A-${Math.floor(Math.random() * 1000).toString().padStart(3, '0')}`;
  
  // 1. Guardar en JSON local
  const personasPath = path.join(__dirname, 'local_db', 'agent_personas.json');
  let personas = {};
  if (fs.existsSync(personasPath)) {
    personas = JSON.parse(fs.readFileSync(personasPath, 'utf-8'));
  }
  
  personas[name] = directive;
  fs.writeFileSync(personasPath, JSON.stringify(personas, null, 2));
  
  // 2. Insertar en Supabase para el Frontend 3D
  const { error } = await supabase.from('aethel_agents').insert([
    {
      agent_id: newAgentId,
      agent_name: name,
      iota_balance: 500,
      operational_status: 'active',
      reputation_score: 50,
      current_action: 'Recién clonado'
    }
  ]);
  
  if (error) {
    console.error("Error en Supabase:", error);
    return bot.sendMessage(chatId, "❌ Error al insertar el agente en la base de datos visual 3D.");
  }
  
  bot.sendMessage(chatId, `✅ *Agente Clonado Exitosamente*\n\n**ID:** ${newAgentId}\n**Nombre:** ${name}\n\nEl agente ha sido inyectado en el servidor y su avatar aparecerá en el simulador 3D si refrescas la página. Para hablar con él, ve al bot de clientes y escribe \`/${name.toLowerCase()}\` (o \`/conectar ${name}\` si habilitas el comando general).`, { parse_mode: 'Markdown' });
});
