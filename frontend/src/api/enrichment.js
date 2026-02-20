/**
 * Data Enrichment API Client
 */
import apiClient from './client';

/**
 * Get available enrichment sources
 */
export async function getEnrichmentSources() {
  const response = await apiClient.get('/enrichment/sources');
  return response.data;
}

/**
 * Preview enrichment for data
 */
export async function previewEnrichment({ data, sources, sampleSize = 5 }) {
  const response = await apiClient.post('/enrichment/preview', {
    data,
    sources,
    sample_size: sampleSize,
  });
  return response.data;
}

/**
 * Enrich data batch
 */
export async function enrichData({ data, sources, options = {} }) {
  const response = await apiClient.post('/enrichment/enrich', {
    data,
    sources,
    options,
  });
  return response.data;
}

/**
 * Create a custom enrichment source
 */
export async function createSource({ name, type, description, config = {}, cacheTtlHours = 24 }) {
  const response = await apiClient.post('/enrichment/sources/create', {
    name,
    type,
    description,
    config,
    cache_ttl_hours: cacheTtlHours,
  });
  return response.data;
}

/**
 * Delete a custom enrichment source
 */
export async function deleteSource(sourceId) {
  const response = await apiClient.delete(`/enrichment/sources/${sourceId}`);
  return response.data;
}

/**
 * Get cache statistics
 */
export async function getCacheStats() {
  const response = await apiClient.get('/enrichment/cache/stats');
  return response.data;
}

/**
 * Clear enrichment cache
 */
export async function clearCache(sourceId = null) {
  const params = sourceId ? `?source_id=${sourceId}` : '';
  const response = await apiClient.delete(`/enrichment/cache${params}`);
  return response.data;
}

export default {
  getEnrichmentSources,
  previewEnrichment,
  enrichData,
  createSource,
  deleteSource,
  getCacheStats,
  clearCache,
};
