/**
 * Search API Client
 * Handles search and discovery operations.
 */
import { api } from './client';

function asArray(payload, keys = []) {
  if (Array.isArray(payload)) return payload;
  if (!payload || typeof payload !== 'object') return [];
  for (const key of keys) {
    if (Array.isArray(payload[key])) return payload[key];
  }
  return [];
}

function normalizeSearchResponse(payload, fallbackQuery = '') {
  if (!payload || typeof payload !== 'object') {
    return { query: fallbackQuery, results: [], total: 0, facets: {} };
  }
  const results = asArray(payload, ['results', 'items', 'documents']);
  const total = payload.total ?? payload.total_results ?? payload.count ?? results.length;
  const rawFacets = payload.facets;
  const facets = Array.isArray(rawFacets)
    ? Object.fromEntries(
        rawFacets
          .filter((entry) => entry && typeof entry === 'object')
          .map((entry, index) => [entry.field || entry.name || `facet_${index}`, entry.values || entry.buckets || []])
      )
    : (rawFacets && typeof rawFacets === 'object' ? rawFacets : {});
  return {
    ...payload,
    query: payload.query ?? fallbackQuery,
    results,
    total,
    facets,
  };
}

// ============================================
// Core Search
// ============================================

export async function search(query, options = {}) {
  const response = await api.post('/search/search', {
    query,
    search_type: options.searchType || 'fulltext',
    filters: options.filters || [],
    page: options.page || 1,
    page_size: options.pageSize || 20,
    highlight: options.highlight !== false,
    facet_fields: options.facets || [],
  });
  return normalizeSearchResponse(response.data, query);
}

export async function semanticSearch(query, options = {}) {
  const response = await api.post('/search/search/semantic', {
    query,
    search_type: 'semantic',
    filters: options.filters || [],
    page: options.page || 1,
    page_size: options.limit || 20,
  });
  return normalizeSearchResponse(response.data, query);
}

export async function regexSearch(pattern, options = {}) {
  const response = await api.post('/search/search/regex', {
    query: pattern,
    search_type: 'regex',
    filters: options.filters || [],
  });
  return normalizeSearchResponse(response.data, pattern);
}

export async function booleanSearch(query, options = {}) {
  const response = await api.post('/search/search/boolean', {
    query,
    search_type: 'boolean',
    filters: options.filters || [],
  });
  return normalizeSearchResponse(response.data, query);
}

// ============================================
// Search & Replace
// ============================================

export async function searchAndReplace(searchQuery, replaceWith, options = {}) {
  const response = await api.post('/search/search/replace', {
    search_query: searchQuery,
    replace_with: replaceWith,
    document_ids: options.documentIds || null,
    dry_run: options.previewOnly !== false,
  });
  return response.data;
}

// ============================================
// Similar Documents
// ============================================

export async function findSimilar(documentId, options = {}) {
  const response = await api.get(`/search/documents/${documentId}/similar`, {
    params: {
      limit: options.limit || 10,
      min_similarity: options.minSimilarity || 0.5,
    },
  });
  return response.data;
}

// ============================================
// Index Management
// ============================================

export async function indexDocument(documentId, title, content, metadata = {}) {
  const response = await api.post('/search/index', {
    document_id: documentId,
    title,
    content,
    metadata,
  });
  return response.data;
}

export async function removeFromIndex(documentId) {
  const response = await api.delete(`/search/index/${documentId}`);
  return response.data;
}

export async function reindexAll() {
  const response = await api.post('/search/index/reindex');
  return response.data;
}

// ============================================
// Saved Searches
// ============================================

export async function saveSearch(name, query, options = {}) {
  const response = await api.post('/search/saved-searches', {
    name,
    query,
    filters: options.filters || [],
    notify_on_new: options.isAlert || false,
  });
  return response.data;
}

export async function listSavedSearches() {
  const response = await api.get('/search/saved-searches');
  return asArray(response.data, ['searches', 'saved_searches', 'items', 'results']);
}

export async function getSavedSearch(searchId) {
  const response = await api.get(`/search/saved-searches/${searchId}`);
  return response.data;
}

export async function deleteSavedSearch(searchId) {
  const response = await api.delete(`/search/saved-searches/${searchId}`);
  return response.data;
}

export async function runSavedSearch(searchId) {
  const response = await api.post(`/search/saved-searches/${searchId}/run`);
  return normalizeSearchResponse(response.data);
}

// ============================================
// Analytics
// ============================================

export async function getSearchAnalytics(options = {}) {
  const response = await api.get('/search/analytics', {
    params: {
      days: options.days || 30,
    },
  });
  return response.data;
}
