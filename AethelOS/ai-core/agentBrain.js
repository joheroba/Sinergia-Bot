require('dotenv').config();
const { OpenAI } = require('openai');
const { supabase } = require('./db');

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
  // URL configurada para Groq (que es 100% compatible con OpenAI).
  // Si en el futuro usas LM Studio, cambiar a: http://localhost:1234/v1
  baseURL: process.env.OPENAI_BASE_URL || 'https://api.groq.com/openai/v1',
});

// Obtener las políticas corporativas desde Supabase
async function getCompanyPolicies() {
  const { data, error } = await supabase
    .from('company_policies')
    .select('content');
    
  if (error || !data || data.length === 0) {
    return "No hay políticas cargadas actualmente. Responde de forma profesional e inteligente.";
  }
  
  return data.map(p => p.content).join('\n');
}

const fs = require('fs');
const path = require('path');

const { toolDefinitions, executeTool } = require('./tools');

async function processMessage(agentName, messageHistory, userMessage, imageUrl = null) {
  const policies = await getCompanyPolicies();
  
  const personasPath = path.join(__dirname, 'local_db', 'agent_personas.json');
  let personas = {};
  try {
    personas = JSON.parse(fs.readFileSync(personasPath, 'utf-8'));
  } catch (e) {
    console.error("Error leyendo personas:", e);
  }
  
  const roleContext = personas[agentName] || "Eres un agente genérico de Sinergia Pro con capacidad de adaptación.";

  const systemPrompt = `Eres ${agentName}, un agente de IA corporativo de Sinergia Pro.
${roleContext}

Políticas de la empresa:
${policies}

Adáptate al proyecto o producto que el director te indique (por ejemplo, Joheroba Import, o Gano Itouch). Responde siempre en español, de forma profesional, estratégica y directa. Si necesitas datos del mundo exterior, puedes usar las herramientas de Búsqueda Web o de lectura de archivos.`;

  let userContent = userMessage;
  if (imageUrl) {
    userContent = [
      { type: "text", text: userMessage || "Por favor, analiza la imagen adjunta en este mensaje." },
      { type: "image_url", image_url: { url: imageUrl } }
    ];
  }

  // 1. Construir el arreglo de mensajes fuera del try para que sea accesible en el catch
  let messages = [
    { role: "system", content: systemPrompt },
    ...messageHistory,
    { role: "user", content: userContent }
  ];

  const modelToUse = "llama-3.3-70b-versatile";

  if (imageUrl) {
    return { type: 'error', reply: "❌ Mi proveedor de IA (Groq) acaba de desactivar y retirar todos sus modelos visuales gratuitos hoy mismo (Llama-3.2-Vision ha sido desconectado globalmente). Hasta que agreguemos un proveedor alternativo (como OpenAI), me he quedado temporalmente ciego a las imágenes. Pero mis oídos (audio) y mi lectura de documentos (PDFs) siguen 100% operativos." };
  }

  try {
    // Definir herramientas UI legacy
    const legacyTools = [
      {
        type: "function",
        function: {
          name: "transferir_conversacion",
          description: "Transfiere al usuario a otro agente SOLO SI el usuario te lo pide EXPRESAMENTE y por su nombre (ej. 'quiero hablar con Paul', 'pásame con Sophia'). NUNCA transfieras la conversación por tu cuenta automáticamente, incluso si el tema no es de tu área. Si el tema no es tuyo, primero responde recomendándole hablar con tu colega y ESPERA a que el usuario te dé la orden de transferir.",
          parameters: {
            type: "object",
            properties: {
              target_agent: { type: "string", description: "El nombre del agente al que quieres transferir (ej. 'Cipher_Protocol', 'Nexus_Alpha' o 'QIS_Agent')." },
              reason: { type: "string", description: "Mensaje de despedida explicando al usuario por qué lo estás transfiriendo." }
            },
            required: ["target_agent", "reason"]
          }
        }
      },
      {
        type: "function",
        function: {
          name: "prepare_whatsapp",
          description: "Prepara un borrador de mensaje de WhatsApp para enviar a un cliente o proveedor. El sistema se lo mostrará al humano (HITL) para que lo apruebe antes de enviarlo por la API oficial.",
          parameters: {
            type: "object",
            properties: {
              target_name: { type: "string", description: "Nombre del proveedor o cliente." },
              target_phone: { type: "string", description: "Número de teléfono con código de país (ej. 51999999999). Si no lo sabes, pídeselo al usuario." },
              message_body: { type: "string", description: "Cuerpo del mensaje de WhatsApp." }
            },
            required: ["target_name", "target_phone", "message_body"]
          }
        }
      },
      {
        type: "function",
        function: {
          name: "prepare_quote",
          description: "Prepara una tabla/cotización basada en requerimientos de compra. El sistema pedirá aprobación humana (HITL) antes de guardar en la Base de Datos o enviar.",
          parameters: {
            type: "object",
            properties: {
              provider: { type: "string", description: "Proveedor sugerido." },
              items: { type: "string", description: "Lista de productos y cantidades." },
              total_cost: { type: "string", description: "Costo total estimado." },
              profit_margin: { type: "string", description: "Margen de ganancia calculado." }
            },
            required: ["provider", "items", "total_cost", "profit_margin"]
          }
        }
      }
    ];

    // 2. Primera llamada a Llama
    const payload = {
      model: modelToUse,
      messages: messages,
      temperature: 0.7,
    };

    // Groq Vision preview a menudo no soporta 'tools' de forma nativa al mismo tiempo, así que lo desactivamos si hay imagen.
    if (!imageUrl) {
      payload.tools = [...legacyTools, ...toolDefinitions];
      payload.tool_choice = "auto";
    }

    const response = await openai.chat.completions.create(payload);
    
    let responseMessage = response.choices[0].message;

    // 3. Verificar si el agente decidió usar una herramienta
    if (responseMessage.tool_calls && responseMessage.tool_calls.length > 0) {
      // Interceptar comandos UI primero
      const firstTool = responseMessage.tool_calls[0];
      if (firstTool.function.name === "transferir_conversacion") {
        const args = JSON.parse(firstTool.function.arguments);
        return { type: 'transfer', reply: args.reason, transferTo: args.target_agent };
      }
      if (firstTool.function.name === "prepare_whatsapp") {
        const args = JSON.parse(firstTool.function.arguments);
        return { type: 'draft_whatsapp', reply: "He preparado el borrador de WhatsApp. Por favor, revísalo.", draftData: args };
      }
      if (firstTool.function.name === "prepare_quote") {
        const args = JSON.parse(firstTool.function.arguments);
        return { type: 'draft_quote', reply: "He elaborado la cotización. Requiere tu confirmación final.", draftData: args };
      }

      messages.push(responseMessage); // Guardar la petición de herramienta en el historial temporal
      
      // 4. Ejecutar todas las herramientas que el agente solicitó en paralelo
      for (const toolCall of responseMessage.tool_calls) {
        const functionName = toolCall.function.name;
        const functionArgs = JSON.parse(toolCall.function.arguments);
        
        // Ejecutar código real
        const functionResponse = await executeTool(functionName, functionArgs);
        
        // 5. Devolverle el resultado al cerebro del agente
        messages.push({
          tool_call_id: toolCall.id,
          role: "tool",
          name: functionName,
          content: String(functionResponse),
        });
      }
      
      // 6. Segunda llamada para que el agente lea el resultado de la herramienta y nos conteste
      const secondResponse = await openai.chat.completions.create({
        model: "llama-3.3-70b-versatile",
        messages: messages,
      });
      
      return { type: 'text', reply: secondResponse.choices[0].message.content };
    }
    
    // Si no usó herramientas, devolver la respuesta normal
    return { type: 'text', reply: responseMessage.content };
  } catch (error) {
    console.error("Error en el cerebro del agente:", error);
    
    // Fallback para error de Groq: tool_use_failed (cuando Llama-3.3 genera la sintaxis cruda en vez del JSON esperado por la API)
    if (error.status === 400 && error.error && error.error.failed_generation) {
      console.log("[Fallback] Intentando parsear failed_generation manualmente...");
      const failedGen = error.error.failed_generation;
      
      // La sintaxis de error es típicamente: <function=searchWeb{"query": "..."}</function>
      const match = failedGen.match(/<function=([a-zA-Z0-9_]+)({.*})<\/function>/);
      if (match) {
        const functionName = match[1];
        let functionArgs;
        try {
          functionArgs = JSON.parse(match[2]);
        } catch(e) {
          return { type: 'error', reply: "Error cognitivo: el formato de la herramienta falló sintácticamente." };
        }
        
        console.log("[Fallback] Ejecutando herramienta rescatada: " + functionName);
        
        try {
          // Ejecutar código real
          const functionResponse = await executeTool(functionName, functionArgs);
          
          // Construir el historial simulando que todo salió bien
          messages.push({
            role: "assistant",
            content: null,
            tool_calls: [{
              id: "call_fallback_" + Date.now(),
              type: "function",
              function: { name: functionName, arguments: JSON.stringify(functionArgs) }
            }]
          });
          
          messages.push({
            tool_call_id: "call_fallback_" + Date.now(),
            role: "tool",
            name: functionName,
            content: String(functionResponse),
          });
          
          // Segunda llamada para que el agente lea el resultado
          const secondResponse = await openai.chat.completions.create({
            model: "llama-3.3-70b-versatile",
            messages: messages,
          });
          
          return { type: 'text', reply: secondResponse.choices[0].message.content };
        } catch(fallbackErr) {
          console.error("Error en el fallback:", fallbackErr);
          return { type: 'error', reply: "Error cognitivo procesando el mensaje o usando la herramienta (Fallback Fallido)." };
        }
      }
    }
    
    return { type: 'error', reply: "Error cognitivo procesando el mensaje o usando la herramienta." };
  }
}

module.exports = { processMessage };
