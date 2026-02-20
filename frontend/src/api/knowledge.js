/**
 * Knowledge API Client
 * Handles document library, collections, and knowledge management.
 */
import { api } from './client';

function normalizeDocument(doc) {
  if (!doc || typeof doc !== 'object') return doc;
  const normalized = { ...doc };
  if (normalized.file_type == null && normalized.document_type) {
    normalized.file_type = normalized.document_type;
  }
  if (normalized.collection_ids == null && Array.isArray(normalized.collections)) {
    normalized.collection_ids = normalized.collections;
  }
  return normalized;
}

function inferDocumentType(fileName) {
  const ext = String(fileName || '').toLowerCase().split('.').pop();
  switch (ext) {
    case 'pdf':
      return 'pdf';
    case 'doc':
    case 'docx':
      return 'docx';
    case 'xls':
    case 'xlsx':
      return 'xlsx';
    case 'ppt':
    case 'pptx':
      return 'pptx';
    case 'txt':
      return 'txt';
    case 'md':
    case 'markdown':
      return 'md';
    case 'htm':
    case 'html':
      return 'html';
    case 'png':
    case 'jpg':
    case 'jpeg':
    case 'gif':
    case 'webp':
      return 'image';
    default:
      return 'other';
  }
}

// ============================================
// Documents
// ============================================

export async function addDocument(data) {
  const response = await api.post('/knowledge/documents', data);
  return response.data;
}

export async function uploadDocument(file, title, collectionId = null) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('title', title || file.name);
  formData.append('document_type', inferDocumentType(file?.name));
  if (collectionId) {
    formData.append('collection_id', collectionId);
  }
  const response = await api.post('/knowledge/documents', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

export async function getDocument(documentId) {
  const response = await api.get(`/knowledge/documents/${documentId}`);
  return response.data;
}

export async function listDocuments(options = {}) {
  const response = await api.get('/knowledge/documents', {
    params: {
      collection_id: options.collectionId,
      tags: Array.isArray(options.tags) ? options.tags.join(',') : options.tags,
      document_type: options.documentType,
      limit: options.pageSize || 50,
      offset: options.offset || 0,
    },
  });
  const payload = response.data;
  if (Array.isArray(payload)) {
    const documents = payload.map(normalizeDocument);
    return { documents, total: documents.length };
  }
  if (payload && Array.isArray(payload.documents)) {
    const documents = payload.documents.map(normalizeDocument);
    return { ...payload, documents, total: payload.total ?? documents.length };
  }
  return { documents: [], total: 0 };
}

export async function updateDocument(documentId, data) {
  const response = await api.put(`/knowledge/documents/${documentId}`, data);
  return response.data;
}

export async function deleteDocument(documentId) {
  const response = await api.delete(`/knowledge/documents/${documentId}`);
  return response.data;
}

export async function toggleFavorite(documentId) {
  const response = await api.post(`/knowledge/documents/${documentId}/favorite`);
  return response.data;
}

// ============================================
// Collections
// ============================================

export async function createCollection(data) {
  const response = await api.post('/knowledge/collections', data);
  return response.data;
}

export async function getCollection(collectionId) {
  const response = await api.get(`/knowledge/collections/${collectionId}`);
  return response.data;
}

export async function listCollections() {
  const response = await api.get('/knowledge/collections');
  const payload = response.data;
  if (Array.isArray(payload)) return payload;
  if (payload && typeof payload === 'object') {
    return Array.isArray(payload.collections) ? payload.collections : [];
  }
  return [];
}

export async function updateCollection(collectionId, data) {
  const response = await api.put(`/knowledge/collections/${collectionId}`, data);
  return response.data;
}

export async function deleteCollection(collectionId) {
  const response = await api.delete(`/knowledge/collections/${collectionId}`);
  return response.data;
}

export async function addDocumentToCollection(collectionId, documentId) {
  const response = await api.post(`/knowledge/collections/${collectionId}/documents`, {
    document_id: documentId,
  });
  return response.data;
}

export async function removeDocumentFromCollection(collectionId, documentId) {
  const response = await api.delete(`/knowledge/collections/${collectionId}/documents/${documentId}`);
  return response.data;
}

// ============================================
// Tags
// ============================================

export async function createTag(name, color = null) {
  const response = await api.post('/knowledge/tags', { name, color });
  return response.data;
}

export async function listTags() {
  const response = await api.get('/knowledge/tags');
  const payload = response.data;
  if (Array.isArray(payload)) return payload;
  if (payload && typeof payload === 'object') {
    return Array.isArray(payload.tags) ? payload.tags : [];
  }
  return [];
}

export async function deleteTag(tagId) {
  const response = await api.delete(`/knowledge/tags/${tagId}`);
  return response.data;
}

export async function addTagToDocument(documentId, tagId) {
  const response = await api.post(`/knowledge/documents/${documentId}/tags`, {
    tag_id: tagId,
  });
  return response.data;
}

export async function removeTagFromDocument(documentId, tagId) {
  const response = await api.delete(`/knowledge/documents/${documentId}/tags/${tagId}`);
  return response.data;
}

// ============================================
// Search
// ============================================

export async function searchDocuments(query, options = {}) {
  const response = await api.post('/knowledge/search', {
    query,
    collections: options.collectionId ? [options.collectionId] : [],
    tags: options.tags || [],
    date_from: options.dateFrom,
    date_to: options.dateTo,
    limit: options.pageSize || 50,
    offset: options.offset || 0,
  });
  return response.data;
}

export async function semanticSearch(query, options = {}) {
  const response = await api.post('/knowledge/search/semantic', {
    query,
    top_k: options.limit || 10,
    threshold: options.minSimilarity || 0.5,
  });
  return response.data;
}

// ============================================
// AI Features
// ============================================

export async function autoTag(documentId, maxTags = 5) {
  const response = await api.post('/knowledge/auto-tag', {
    document_id: documentId,
    max_tags: maxTags,
  });
  return response.data;
}

export async function findRelated(documentId, options = {}) {
  const response = await api.post('/knowledge/related', {
    document_id: documentId,
    limit: options.limit || 10,
  });
  return response.data;
}

export async function buildKnowledgeGraph(options = {}) {
  const response = await api.post('/knowledge/knowledge-graph', {
    document_ids: options.documentIds || [],
    depth: options.depth || 2,
    include_entities: options.includeEntities !== false,
  });
  return response.data;
}

export async function generateFaq(options = {}) {
  const documentIds = Array.isArray(options.documentIds)
    ? options.documentIds.filter(Boolean)
    : [];
  const response = await api.post('/knowledge/faq', {
    document_ids: documentIds,
    max_questions: options.maxQuestions || 10,
  }, {
    params: {
      background: options.background ?? false,
    },
  });
  return response.data;
}

// ============================================
// Analytics
// ============================================

export async function getLibraryStats() {
  const response = await api.get('/knowledge/stats');
  return response.data;
}

export async function getDocumentActivity(documentId, options = {}) {
  const response = await api.get(`/knowledge/documents/${documentId}/activity`, {
    params: {
      days: options.days || 30,
    },
  });
  return response.data;
}
