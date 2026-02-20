/**
 * Ingestion API Client
 * Handles document ingestion and import operations.
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
// File Upload
// ============================================

export async function uploadFile(file, options = {}) {
  const formData = new FormData();
  formData.append('file', file);
  if (options.autoDetect !== false) {
    formData.append('auto_ocr', 'true');
  }
  if (options.generatePreview !== false) {
    formData.append('generate_preview', 'true');
  }
  if (options.tags) {
    formData.append('tags', options.tags);
  }
  if (options.collection) {
    formData.append('collection', options.collection);
  }

  const response = await api.post('/ingestion/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: options.onProgress,
  });
  return response.data;
}

export async function uploadBulk(files, options = {}) {
  const formData = new FormData();
  files.forEach((file, index) => {
    formData.append(`files`, file);
  });
  if (options.autoDetect !== false) {
    formData.append('auto_detect', 'true');
  }

  const response = await api.post('/ingestion/upload/bulk', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: options.onProgress,
  });
  const payload = response.data;
  if (Array.isArray(payload)) return payload;
  if (payload && typeof payload === 'object') {
    return asArray(payload, ['results', 'uploads', 'files', 'items']);
  }
  return [];
}

export async function uploadZip(file, options = {}) {
  const formData = new FormData();
  formData.append('file', file);
  if (options.flattenFolders) {
    formData.append('flatten_folders', 'true');
  }

  const response = await api.post('/ingestion/upload/zip', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: options.onProgress,
  });
  return response.data;
}

// ============================================
// URL Import
// ============================================

export async function importFromUrl(url, options = {}) {
  const response = await api.post('/ingestion/url', {
    url,
    extract_text: options.extractText !== false,
    follow_links: options.followLinks || false,
    max_depth: options.maxDepth || 1,
  });
  return response.data;
}

// ============================================
// Structured Data Import
// ============================================

export async function importStructuredData(data, format, options = {}) {
  const response = await api.post('/ingestion/structured', {
    content: typeof data === 'string' ? data : JSON.stringify(data),
    filename: options.filename || `import.${format || 'json'}`,
    format_hint: format || null,
  });
  return response.data;
}

// ============================================
// Web Clipper
// ============================================

export async function clipUrl(url, options = {}) {
  const response = await api.post('/ingestion/clip/url', {
    url,
    include_images: options.includeImages !== false,
    clean_content: options.cleanContent !== false,
    capture_screenshot: options.captureScreenshot || false,
  });
  return response.data;
}

export async function clipSelection(content, sourceUrl, options = {}) {
  const response = await api.post('/ingestion/clip/selection', {
    selected_html: content,
    url: sourceUrl,
    page_title: options.title || null,
  });
  return response.data;
}

// ============================================
// Folder Watchers
// ============================================

export async function createWatcher(folderPath, options = {}) {
  const response = await api.post('/ingestion/watchers', {
    path: folderPath,
    patterns: options.patterns || ['*'],
    recursive: options.recursive !== false,
    auto_import: options.autoImport !== false,
    delete_after_import: options.deleteAfterImport || false,
    target_collection: options.targetCollection || null,
    ignore_patterns: options.ignorePatterns || [],
    tags: options.tags || [],
  });
  return response.data;
}

export async function listWatchers() {
  const response = await api.get('/ingestion/watchers');
  return asArray(response.data, ['watchers', 'items', 'results']);
}

export async function getWatcher(watcherId) {
  const response = await api.get(`/ingestion/watchers/${watcherId}`);
  return response.data;
}

export async function startWatcher(watcherId) {
  const response = await api.post(`/ingestion/watchers/${watcherId}/start`);
  return response.data;
}

export async function stopWatcher(watcherId) {
  const response = await api.post(`/ingestion/watchers/${watcherId}/stop`);
  return response.data;
}

export async function deleteWatcher(watcherId) {
  const response = await api.delete(`/ingestion/watchers/${watcherId}`);
  return response.data;
}

export async function scanFolder(watcherId) {
  const response = await api.post(`/ingestion/watchers/${watcherId}/scan`);
  return response.data;
}

// ============================================
// Transcription
// ============================================

export async function transcribeFile(file, options = {}) {
  const formData = new FormData();
  formData.append('file', file);
  if (options.language) {
    formData.append('language', options.language);
  }
  if (options.model) {
    formData.append('model', options.model);
  }
  if (options.timestamps) {
    formData.append('timestamps', 'true');
  }

  const response = await api.post('/ingestion/transcribe', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: options.onProgress,
  });
  return response.data;
}

export async function getTranscriptionStatus(jobId) {
  const response = await api.get(`/ingestion/transcribe/${jobId}`);
  return response.data;
}

// ============================================
// Email Import
// ============================================

export async function parseEmail(emailFile, options = {}) {
  const formData = new FormData();
  formData.append('file', emailFile);
  formData.append('extract_action_items', options.extractActionItems !== false ? 'true' : 'false');

  const response = await api.post('/ingestion/email/parse', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

export async function connectImapAccount(config) {
  const response = await api.post('/ingestion/email/imap/connect', config);
  return response.data;
}

export async function listImapAccounts() {
  const response = await api.get('/ingestion/email/imap/accounts');
  return asArray(response.data, ['accounts', 'items', 'results']);
}

export async function syncImapAccount(accountId, options = {}) {
  const response = await api.post(`/ingestion/email/imap/accounts/${accountId}/sync`, {
    folder: options.folder || 'INBOX',
    since_date: options.sinceDate || null,
    limit: options.limit || 100,
  });
  return response.data;
}
