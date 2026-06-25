const axios = require('axios');
const cheerio = require('cheerio');
const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');

const toolDefinitions = [
  {
    type: "function",
    function: {
      name: "searchWeb",
      description: "Busca información en tiempo real en internet usando DuckDuckGo. Usa esta herramienta cuando necesites investigar tendencias actuales, noticias o precios que no sabes.",
      parameters: {
        type: "object",
        properties: {
          query: {
            type: "string",
            description: "El término de búsqueda (ej. 'Precio de Gano Excel Perú 2026')"
          }
        },
        required: ["query"]
      }
    }
  },
  {
    type: "function",
    function: {
      name: "browseWebPage",
      description: "Navega a una URL específica y extrae el texto de la página. Útil para leer noticias completas o extraer precios de un enlace específico (ej. proveedores).",
      parameters: {
        type: "object",
        properties: {
          url: {
            type: "string",
            description: "La URL completa (ej. 'https://www.deltron.com.pe/...')"
          }
        },
        required: ["url"]
      }
    }
  },
  {
    type: "function",
    function: {
      name: "readFileContent",
      description: "Lee el contenido de un archivo de texto (.txt, .md, .csv) en el servidor local. Útil si el usuario te dice que leas un archivo específico.",
      parameters: {
        type: "object",
        properties: {
          filename: {
            type: "string",
            description: "El nombre del archivo a leer (ej. 'plan_compensacion.txt')"
          }
        },
        required: ["filename"]
      }
    }
  },
  {
    type: "function",
    function: {
      name: "sendEmailMock",
      description: "Simula el envío de un correo electrónico. En esta fase de desarrollo, el correo no se envía de verdad, solo se guarda en una carpeta segura de simulaciones. Usa esto cuando te pidan enviar correos.",
      parameters: {
        type: "object",
        properties: {
          to: { type: "string", description: "El destinatario (ej. 'cliente@gmail.com')" },
          subject: { type: "string", description: "El asunto del correo" },
          body: { type: "string", description: "El cuerpo del correo" }
        },
        required: ["to", "subject", "body"]
      }
    }
  }
];

async function executeTool(toolName, args) {
  try {
    switch(toolName) {
      case "searchWeb":
        return await performSearch(args.query);
      case "browseWebPage":
        return await performBrowse(args.url);
      case "readFileContent":
        return await performReadFile(args.filename);
      case "sendEmailMock":
        return await performSendEmail(args.to, args.subject, args.body);
      default:
        return `Error: Herramienta ${toolName} no reconocida.`;
    }
  } catch (error) {
    return `Error ejecutando la herramienta ${toolName}: ${error.message}`;
  }
}

// WhatsApp API Interna (No es una herramienta LLM directa, es ejecutada por el humano HITL)
async function executeWhatsAppSend(targetPhone, messageBody) {
  const token = process.env.WHATSAPP_TOKEN;
  const phoneId = process.env.WHATSAPP_PHONE_ID;
  
  if (!token || !phoneId) {
    throw new Error("WHATSAPP_TOKEN o WHATSAPP_PHONE_ID no configurados en .env");
  }

  // Limpiar el teléfono para que solo tenga números
  const phone = targetPhone.replace(/\D/g, '');

  const data = {
    messaging_product: "whatsapp",
    to: phone,
    type: "text",
    text: { body: messageBody }
  };

  const response = await axios.post(`https://graph.facebook.com/v19.0/${phoneId}/messages`, data, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });

  return response.data;
}

// Implementación Búsqueda Web
async function performSearch(query) {
  console.log(`[TOOL] Buscando en internet: ${query}`);
  try {
    const response = await axios.get(`https://html.duckduckgo.com/html/?q=${encodeURIComponent(query)}`, {
      headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' }
    });
    const $ = cheerio.load(response.data);
    let results = [];
    $('.result__snippet').each((i, el) => {
      if (i < 5) results.push($(el).text().trim());
    });
    if (results.length === 0) return "No se encontraron resultados en la web. Intenta con browseWebPage.";
    return "Resultados de búsqueda:\n" + results.join('\n');
  } catch(e) {
    return "Falló la búsqueda web estática: " + e.message;
  }
}

// Implementación Navegación Real (Puppeteer)
async function performBrowse(url) {
  console.log(`[TOOL] Navegando página web: ${url}`);
  let browser;
  try {
    browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox', '--disable-setuid-sandbox'] });
    const page = await browser.newPage();
    await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
    
    // Extraer texto visible
    const text = await page.evaluate(() => document.body.innerText);
    await browser.close();
    
    // Devolver los primeros 5000 caracteres para no saturar al agente
    return text.substring(0, 5000);
  } catch(e) {
    if (browser) await browser.close();
    return "Falló la extracción visual de Puppeteer: " + e.message;
  }
}

// Implementación Leer Archivo
async function performReadFile(filename) {
  console.log(`[TOOL] Leyendo archivo: ${filename}`);
  const docsFolder = path.join(__dirname, '..', '..', 'brain'); 
  // Intentamos buscarlo recursivamente en el directorio del usuario para mayor flexibilidad
  const filePath = path.join(__dirname, '..', '..', 'brain', '9eb4ec31-d5ce-4bc5-a7d0-c09eb14cbb2d', filename);
  
  if (fs.existsSync(filePath)) {
    return fs.readFileSync(filePath, 'utf-8');
  } else {
    // Buscar en el directorio actual también por si acaso
    const localPath = path.join(__dirname, filename);
    if(fs.existsSync(localPath)) return fs.readFileSync(localPath, 'utf-8');
    
    return `Error: No se encontró el archivo ${filename}. Dile al usuario que asegure el nombre del archivo.`;
  }
}

// Implementación Enviar Correo Mock
async function performSendEmail(to, subject, body) {
  console.log(`[TOOL] Enviando correo a ${to}`);
  const draftsFolder = path.join(__dirname, 'correos_simulados');
  if (!fs.existsSync(draftsFolder)) {
    fs.mkdirSync(draftsFolder);
  }
  
  const mailContent = `PARA: ${to}\nASUNTO: ${subject}\n\nCUERPO:\n${body}`;
  const fileName = `correo_${Date.now()}.txt`;
  fs.writeFileSync(path.join(draftsFolder, fileName), mailContent);
  
  return `¡Correo guardado exitosamente en el buzón seguro de simulaciones! Dile al usuario que el correo fue enviado en modo seguro.`;
}

module.exports = {
  toolDefinitions,
  executeTool,
  executeWhatsAppSend
};
