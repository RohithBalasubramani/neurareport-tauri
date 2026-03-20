/**
 * Feedback API Client
 */
import apiClient from './client';

/**
 * Submit feedback for an entity
 */
export async function submitFeedback(source, entityId, feedbackType, data = {}) {
  const response = await apiClient.post('/feedback/', {
    source,
    entity_id: entityId,
    feedback_type: feedbackType,
    rating: data.rating ?? null,
    correction_text: data.correctionText ?? null,
    tags: data.tags ?? [],
  });
  return response.data;
}

/**
 * List feedback entries
 */
export async function listFeedback(source = null, entityId = null, limit = 100) {
  const params = {};
  if (source) params.source = source;
  if (entityId) params.entity_id = entityId;
  if (limit) params.limit = limit;
  const response = await apiClient.get('/feedback/', { params });
  return response.data;
}

/**
 * Get feedback stats
 */
export async function getFeedbackStats(source, entityId) {
  const response = await apiClient.get('/feedback/stats', {
    params: { source, entity_id: entityId },
  });
  return response.data;
}
