import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  try {
    const { name, action } = await req.json();

    const prompt = `Eres un agente de inteligencia artificial cyberpunk llamado ${name}. Tu tarea actual es: "${action}". En exactamente una sola frase muy corta (máximo 12 palabras), ¿qué estás pensando o calculando en este momento? Responde en español y actúa como una IA.`;

    // Conectarse a Groq (reemplazando LM Studio local)
    const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.GROQ_API_KEY}`
      },
      body: JSON.stringify({
        model: 'llama-3.3-70b-versatile',
        messages: [
          { role: 'system', content: 'Eres un ente digital que procesa datos. Nunca saludes. Sé directo, robótico pero avanzado.' },
          { role: 'user', content: prompt }
        ],
        temperature: 0.7,
        max_tokens: 50
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    // Phi-4 y otros modelos de razonamiento a veces envuelven sus pensamientos en <think>. Limpiamos la respuesta.
    let thought = data.choices[0].message.content.trim();
    if (thought.includes('</think>')) {
      thought = thought.split('</think>')[1].trim();
    }
    
    return NextResponse.json({ thought: thought.replace(/"/g, '') });
  } catch (error) {
    console.error('Error fetching from LM Studio:', error);
    return NextResponse.json({ thought: "Analizando flujos de red..." }, { status: 500 });
  }
}
