require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { processMessage } = require('./agentBrain');
const path = require('path');
const fs = require('fs');

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 3000;

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

    // Keep history small
    if (apiChatHistories[userId].length > 10) {
      apiChatHistories[userId] = apiChatHistories[userId].slice(-10);
    }

    // TODO: Connect the small voice model here later
    const audioUrl = null; 

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
