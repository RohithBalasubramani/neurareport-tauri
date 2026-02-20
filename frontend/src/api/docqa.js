/**
 * Document Q&A Chat API Client
 */
import apiClient from './client';

function asArray(payload, keys = []) {
  if (Array.isArray(payload)) return payload;
  if (!payload || typeof payload !== 'object') return [];
  for (const key of keys) {
    if (Array.isArray(payload[key])) return payload[key];
  }
  return [];
}

/**
 * Create a Q&A session
 */
export async function createSession(name) {
  const response = await apiClient.post('/docqa/sessions', { name });
  return response.data;
}

/**
 * List all Q&A sessions
 */
export async function listSessions({ limit, offset } = {}) {
  const params = {};
  if (limit != null) params.limit = limit;
  if (offset != null) params.offset = offset;
  const response = await apiClient.get('/docqa/sessions', { params });
  const payload = response.data;
  if (Array.isArray(payload)) {
    return { sessions: payload, total: payload.length };
  }
  if (payload && typeof payload === 'object') {
    const sessions = asArray(payload, ['sessions', 'items', 'results']);
    return { ...payload, sessions, total: payload.total ?? sessions.length };
  }
  return { sessions: [], total: 0 };
}

/**
 * Get a Q&A session
 */
export async function getSession(sessionId) {
  const response = await apiClient.get(`/docqa/sessions/${sessionId}`);
  return response.data;
}

/**
 * Delete a Q&A session
 */
export async function deleteSession(sessionId) {
  const response = await apiClient.delete(`/docqa/sessions/${sessionId}`);
  return response.data;
}

/**
 * Add document to session
 */
export async function addDocument(sessionId, { name, content, pageCount }) {
  const response = await apiClient.post(`/docqa/sessions/${sessionId}/documents`, {
    name,
    content,
    page_count: pageCount,
  });
  return response.data;
}

/**
 * Remove document from session
 */
export async function removeDocument(sessionId, documentId) {
  const response = await apiClient.delete(`/docqa/sessions/${sessionId}/documents/${documentId}`);
  return response.data;
}

/**
 * Ask a question
 */
export async function askQuestion(sessionId, { question, includeCitations = true, maxResponseLength = 2000 }) {
  const response = await apiClient.post(`/docqa/sessions/${sessionId}/ask`, {
    question,
    include_citations: includeCitations,
    max_response_length: maxResponseLength,
  });
  return response.data;
}

/**
 * Get chat history
 */
export async function getChatHistory(sessionId, limit = 50) {
  const response = await apiClient.get(`/docqa/sessions/${sessionId}/history`, {
    params: { limit },
  });
  return response.data;
}

/**
 * Clear chat history
 */
export async function clearHistory(sessionId) {
  const response = await apiClient.delete(`/docqa/sessions/${sessionId}/history`);
  return response.data;
}

/**
 * Submit feedback for a message
 * @param {string} sessionId - Session ID
 * @param {string} messageId - Message ID
 * @param {object} feedback - Feedback data { feedbackType: 'helpful' | 'not_helpful', comment?: string }
 */
export async function submitFeedback(sessionId, messageId, { feedbackType, comment }) {
  const response = await apiClient.post(
    `/docqa/sessions/${sessionId}/messages/${messageId}/feedback`,
    {
      feedback_type: feedbackType,
      comment,
    }
  );
  return response.data;
}

/**
 * Regenerate a response for a message
 * @param {string} sessionId - Session ID
 * @param {string} messageId - Message ID
 * @param {object} options - Options { includeCitations?: boolean, maxResponseLength?: number }
 */
export async function regenerateResponse(sessionId, messageId, { includeCitations = true, maxResponseLength = 2000 } = {}) {
  const response = await apiClient.post(
    `/docqa/sessions/${sessionId}/messages/${messageId}/regenerate`,
    {
      include_citations: includeCitations,
      max_response_length: maxResponseLength,
    }
  );
  return response.data;
}

export default {
  createSession,
  listSessions,
  getSession,
  deleteSession,
  addDocument,
  removeDocument,
  askQuestion,
  getChatHistory,
  clearHistory,
  submitFeedback,
  regenerateResponse,
};
