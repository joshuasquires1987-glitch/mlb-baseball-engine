const express = require('express');
const router = express.Router();
const chatgptService = require('../services/chatgptService');

// POST /api/chat/message
router.post('/message', async (req, res) => {
  try {
    const { message, conversationHistory = [] } = req.body;

    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    const result = await chatgptService.chat(message, conversationHistory);

    if (!result.success) {
      return res.status(500).json({ error: result.error });
    }

    res.json({
      message: result.message,
      usage: result.usage
    });
  } catch (error) {
    console.error('Chat endpoint error:', error);
    res.status(500).json({ error: 'Failed to process chat message' });
  }
});

// POST /api/chat/analyze-player
router.post('/analyze-player', async (req, res) => {
  try {
    const { playerData } = req.body;

    if (!playerData) {
      return res.status(400).json({ error: 'Player data is required' });
    }

    const result = await chatgptService.analyzePlayer(playerData);

    if (!result.success) {
      return res.status(500).json({ error: result.error });
    }

    res.json({
      analysis: result.analysis
    });
  } catch (error) {
    console.error('Player analysis endpoint error:', error);
    res.status(500).json({ error: 'Failed to analyze player' });
  }
});

module.exports = router;
