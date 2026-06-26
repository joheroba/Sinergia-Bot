require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { processMessage } = require('./agentBrain');
const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');
const crypto = require('crypto');

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 3000;

// Servir archivos estáticos de audio
const audioDir = path.join(__dirname, 'public', 'audio');
if (!fs.existsSync(audioDir)) {
  fs.mkdirSync(audioDir, { recursive: true });
}
app.use('/audio', express.static(audioDir));

// Simple memory store for API chat histories
const apiChatHistories = {};

app.post('/api/chat', async (req, res) => {
  try {
    const { message, userId, agent = "GanoiBot" } = req.body;

    if (!message || !userId) {
      return res.status(400).json({ error: 'message and userId are required' });
    }

    if (!apiChatHistories[userId]) {
      apiChatHistories[userId] = [];
    }

    console.log(`[API] Message from ${userId} to ${agent}: ${message}`);

    // Call the core AI processing
    const result = await processMessage(agent, apiChatHistories[userId], message, null);

    // Save history
    apiChatHistories[userId].push({ role: "user", content: message });
    apiChatHistories[userId].push({ role: "assistant", content: result.reply });

    if (apiChatHistories[userId].length > 10) {
      apiChatHistories[userId] = apiChatHistories[userId].slice(-10);
    }

    let audioUrl = null; 

    // Generate Audio using Piper
    const modelPath = path.join(__dirname, 'voice_model', 'modelo_pequeno.onnx');
    const piperBin = path.join(__dirname, 'piper', 'piper'); // piper binary path

    if (fs.existsSync(modelPath) && fs.existsSync(piperBin)) {
      const textToSpeak = result.reply.replace(/"/g, "'"); // basic escape
      const audioFileName = `voice_${crypto.randomBytes(4).toString('hex')}.wav`;
      const audioOutputPath = path.join(audioDir, audioFileName);

      // We echo the text to piper
      const piperCmd = `echo "${textToSpeak}" | "${piperBin}" --model "${modelPath}" --output_file "${audioOutputPath}"`;
      
      try {
        await new Promise((resolve, reject) => {
          exec(piperCmd, (error, stdout, stderr) => {
            if (error) {
              console.error("[API] Piper Execution Error:", stderr);
              reject(error);
            } else {
              resolve();
            }
          });
        });
        
        // Reemplazar IP por el del VPS para la app móvil
        const serverIp = process.env.VPS_IP || '45.55.92.211';
        audioUrl = `http://${serverIp}:${PORT}/audio/${audioFileName}`;
      } catch (err) {
        console.error("Failed to generate audio.");
      }
    } else {
      console.log("[API] Piper binary or model not found. Skipping audio generation.");
    }

    return res.json({
      reply: result.reply,
      type: result.type,
      audioUrl: audioUrl
    });

  } catch (error) {
    console.error('[API] Error processing chat:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'AethelOS API', activeAgent: 'GanoiBot' });
});

app.listen(PORT, () => {
  console.log(`🚀 AethelOS API Server listening on port ${PORT}`);
});
