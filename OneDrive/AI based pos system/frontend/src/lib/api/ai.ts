import axios from 'axios';

const aiClient = axios.create({
  baseURL: 'https://openrouter.ai/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include API key
aiClient.interceptors.request.use((config) => {
  const apiKey = process.env.NEXT_PUBLIC_OPENROUTER_API_KEY;
  if (apiKey) {
    config.headers['Authorization'] = `Bearer ${apiKey}`;
  }
  return config;
});

export interface AIMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface AIResponse {
  id: string;
  content: string;
}

/**
 * Generates an AI response using the OpenRouter API
 * @param messages Array of messages in the conversation
 * @param contextInfo Optional context information about the current state
 * @returns Promise with the AI response
 */
export async function generateAIResponse(
  messages: AIMessage[],
  contextInfo?: Record<string, any>
): Promise<AIResponse> {
  try {
    // Add system message with context if provided
    const allMessages = contextInfo
      ? [
          {
            role: 'system' as const,
            content: `You are an AI assistant for a POS system. Current context: ${JSON.stringify(contextInfo)}`,
          },
          ...messages,
        ]
      : messages;

    const response = await aiClient.post('/chat/completions', {
      model: 'openai/gpt-4-turbo',
      messages: allMessages,
    });

    return {
      id: response.data.id,
      content: response.data.choices[0].message.content,
    };
  } catch (error) {
    console.error('Error generating AI response:', error);
    throw new Error('Failed to generate AI response');
  }
}