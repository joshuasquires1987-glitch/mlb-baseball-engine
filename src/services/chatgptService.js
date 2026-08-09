const { OpenAI } = require('openai');

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

const SYSTEM_PROMPT = `You are an expert MLB baseball analyst with deep knowledge of:
- MLB statistics and player performance
- Historical baseball data and records
- Game strategy and analysis
- Team performance metrics
- Player comparisons and rankings

Provide accurate, insightful baseball analysis and answer questions about MLB comprehensively.`;

async function chat(userMessage, conversationHistory = []) {
  try {
    const messages = [
      ...conversationHistory,
      { role: 'user', content: userMessage }
    ];

    const response = await client.chat.completions.create({
      model: 'gpt-4',
      messages: [
        { role: 'system', content: SYSTEM_PROMPT },
        ...messages
      ],
      temperature: 0.7,
      max_tokens: 1500
    });

    const assistantMessage = response.choices[0].message.content;

    return {
      success: true,
      message: assistantMessage,
      usage: {
        prompt_tokens: response.usage.prompt_tokens,
        completion_tokens: response.usage.completion_tokens,
        total_tokens: response.usage.total_tokens
      }
    };
  } catch (error) {
    console.error('ChatGPT Service Error:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

async function analyzePlayer(playerData) {
  try {
    const prompt = `Analyze this MLB player's statistics and provide insights:
Player: ${playerData.name}
Position: ${playerData.position}
Team: ${playerData.team}
Stats: ${JSON.stringify(playerData.stats, null, 2)}

Provide a comprehensive analysis including strengths, weaknesses, and performance trends.`;

    const response = await client.chat.completions.create({
      model: 'gpt-4',
      messages: [
        { role: 'system', content: SYSTEM_PROMPT },
        { role: 'user', content: prompt }
      ],
      temperature: 0.7,
      max_tokens: 1500
    });

    return {
      success: true,
      analysis: response.choices[0].message.content
    };
  } catch (error) {
    console.error('Player Analysis Error:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

module.exports = {
  chat,
  analyzePlayer
};
