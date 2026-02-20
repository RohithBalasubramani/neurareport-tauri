/**
 * Documents API Client
 * Handles document editing, collaboration, PDF operations, and AI writing features.
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

// ============================================
// Document CRUD
// ============================================

export async function createDocument(data) {
  const response = await api.post('/documents', data);
  return response.data;
}

export async function getDocument(documentId) {
  const response = await api.get(`/documents/${documentId}`);
  return response.data;
}

export async function updateDocument(documentId, data) {
  const response = await api.put(`/documents/${documentId}`, data);
  return response.data;
}

export async function deleteDocument(documentId) {
  const response = await api.delete(`/documents/${documentId}`);
  return response.data;
}

export async function listDocuments(params = {}) {
  const response = await api.get('/documents', { params });
  const payload = response.data;
  if (Array.isArray(payload)) {
    return { documents: payload, total: payload.length };
  }
  if (payload && typeof payload === 'object') {
    const documents = asArray(payload, ['documents', 'items', 'results']);
    return { ...payload, documents, total: payload.total ?? documents.length };
  }
  return { documents: [], total: 0 };
}

// ============================================
// Version History
// ============================================

export async function getVersions(documentId) {
  const response = await api.get(`/documents/${documentId}/versions`);
  return response.data;
}

export async function getVersion(documentId, versionId) {
  const response = await api.get(`/documents/${documentId}/versions/${versionId}`);
  return response.data;
}

export async function restoreVersion(documentId, versionId) {
  const response = await api.post(`/documents/${documentId}/versions/${versionId}/restore`);
  return response.data;
}

// ============================================
// Comments
// ============================================

export async function getComments(documentId) {
  const response = await api.get(`/documents/${documentId}/comments`);
  return response.data;
}

export async function addComment(documentId, data) {
  const response = await api.post(`/documents/${documentId}/comments`, data);
  return response.data;
}

export async function replyToComment(documentId, commentId, data) {
  const response = await api.post(`/documents/${documentId}/comments/${commentId}/reply`, data);
  return response.data;
}

export async function resolveComment(documentId, commentId, resolved = true) {
  const response = await api.patch(`/documents/${documentId}/comments/${commentId}/resolve`, { resolved });
  return response.data;
}

export async function deleteComment(documentId, commentId) {
  const response = await api.delete(`/documents/${documentId}/comments/${commentId}`);
  return response.data;
}

// ============================================
// Collaboration
// ============================================

export async function startCollaboration(documentId, data = {}) {
  const response = await api.post(`/documents/${documentId}/collaborate`, data);
  return response.data;
}

export async function getCollaborators(documentId) {
  const response = await api.get(`/documents/${documentId}/collaborate/presence`);
  return response.data;
}

export async function updatePresence(documentId, data) {
  const response = await api.put(`/documents/${documentId}/presence`, data);
  return response.data;
}

// ============================================
// PDF Operations
// ============================================

export async function reorderPages(documentId, pageOrder) {
  const response = await api.post(`/documents/${documentId}/pdf/reorder`, { page_order: pageOrder });
  return response.data;
}

export async function addWatermark(documentId, data) {
  const response = await api.post(`/documents/${documentId}/pdf/watermark`, data);
  return response.data;
}

export async function redactRegions(documentId, regions) {
  const response = await api.post(`/documents/${documentId}/pdf/redact`, { regions });
  return response.data;
}

export async function mergePdfs(documentIds) {
  const response = await api.post('/documents/merge', { document_ids: documentIds });
  return response.data;
}

export async function splitPdf(documentId, pages) {
  const response = await api.post(`/documents/${documentId}/pdf/split`, { pages });
  return response.data;
}

export async function rotatePdf(documentId, pageRotations) {
  const response = await api.post(`/documents/${documentId}/pdf/rotate`, { page_rotations: pageRotations });
  return response.data;
}

// ============================================
// AI Writing Features
// ============================================

export async function checkGrammar(documentId, text, options = {}) {
  const response = await api.post(`/documents/${documentId}/ai/grammar`, { text, options });
  return response.data;
}

export async function summarize(documentId, text, length = 'medium', style = 'paragraph') {
  const response = await api.post(`/documents/${documentId}/ai/summarize`, {
    text,
    instruction: 'summarize',
    options: { length, style },
  });
  return response.data;
}

export async function rewrite(documentId, text, tone = 'professional', style = 'clear') {
  const response = await api.post(`/documents/${documentId}/ai/rewrite`, {
    text,
    instruction: 'rewrite',
    options: { tone, style },
  });
  return response.data;
}

export async function expand(documentId, text, targetLength = 'double') {
  const response = await api.post(`/documents/${documentId}/ai/expand`, {
    text,
    instruction: 'expand',
    options: { target_length: targetLength },
  });
  return response.data;
}

export async function translate(documentId, text, targetLanguage, preserveFormatting = true) {
  const response = await api.post(`/documents/${documentId}/ai/translate`, {
    text,
    instruction: 'translate',
    options: { target_language: targetLanguage, preserve_formatting: preserveFormatting },
  });
  return response.data;
}

export async function adjustTone(documentId, text, targetTone) {
  const response = await api.post(`/documents/${documentId}/ai/tone`, { text, target_tone: targetTone });
  return response.data;
}

// ============================================
// Templates
// ============================================

export async function listTemplates(params = {}) {
  const response = await api.get('/documents/templates', { params });
  const payload = response.data;
  if (Array.isArray(payload)) {
    return { templates: payload, total: payload.length };
  }
  if (payload && typeof payload === 'object') {
    const templates = asArray(payload, ['templates', 'items', 'results']);
    return { ...payload, templates, total: payload.total ?? templates.length };
  }
  return { templates: [], total: 0 };
}

export async function createFromTemplate(templateId, name) {
  const response = await api.post(`/documents/templates/${templateId}/create`, { name });
  return response.data;
}

export async function saveAsTemplate(documentId, name) {
  const response = await api.post(`/documents/${documentId}/save-as-template`, { name });
  return response.data;
}

// ============================================
// Export
// ============================================

export async function exportDocument(documentId, format) {
  const response = await api.get(`/documents/${documentId}/export`, {
    params: { format },
    responseType: 'blob',
  });
  return response.data;
}
