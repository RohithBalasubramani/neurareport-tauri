/**
 * Export API Client
 * Handles document export and distribution operations.
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
// Export Formats
// ============================================

export async function exportToPdf(documentId, options = {}) {
  const response = await api.post(`/export/${documentId}/pdf`, options, {
    responseType: options.returnBlob ? 'blob' : 'json',
  });
  return response.data;
}

export async function exportToPdfA(documentId, options = {}) {
  const response = await api.post(`/export/${documentId}/pdfa`, options, {
    responseType: options.returnBlob ? 'blob' : 'json',
  });
  return response.data;
}

export async function exportToDocx(documentId, options = {}) {
  const response = await api.post(`/export/${documentId}/docx`, options, {
    responseType: options.returnBlob ? 'blob' : 'json',
  });
  return response.data;
}

export async function exportToPptx(documentId, options = {}) {
  const response = await api.post(`/export/${documentId}/pptx`, options, {
    responseType: options.returnBlob ? 'blob' : 'json',
  });
  return response.data;
}

export async function exportToEpub(documentId, options = {}) {
  const response = await api.post(`/export/${documentId}/epub`, options, {
    responseType: options.returnBlob ? 'blob' : 'json',
  });
  return response.data;
}

export async function exportToLatex(documentId, options = {}) {
  const response = await api.post(`/export/${documentId}/latex`, options);
  return response.data;
}

export async function exportToMarkdown(documentId, options = {}) {
  const response = await api.post(`/export/${documentId}/markdown`, options);
  return response.data;
}

export async function exportToHtml(documentId, options = {}) {
  const response = await api.post(`/export/${documentId}/html`, options);
  return response.data;
}

// ============================================
// Bulk Export
// ============================================

export async function bulkExport(documentIds, format, options = {}) {
  const response = await api.post('/export/bulk', {
    document_ids: documentIds,
    format,
    options,
  });
  return response.data;
}

export async function getBulkExportStatus(jobId) {
  const response = await api.get(`/export/jobs/${jobId}`);
  return response.data;
}

export async function downloadBulkExport(jobId) {
  const response = await api.get(`/export/bulk/${jobId}/download`, {
    responseType: 'blob',
  });
  return response.data;
}

// ============================================
// Distribution
// ============================================

export async function sendEmail(documentIds, options) {
  const response = await api.post('/export/distribution/email-campaign', {
    document_ids: Array.isArray(documentIds) ? documentIds : [documentIds],
    recipients: options.recipients,
    subject: options.subject,
    message: options.message || options.body || '',
    from_name: options.fromName || null,
    reply_to: options.replyTo || null,
    attach_documents: options.attachDocuments !== false,
    track_opens: options.trackOpens !== false,
  });
  return response.data;
}

export async function sendToSlack(documentId, options) {
  const response = await api.post('/export/distribution/slack', {
    document_id: documentId,
    channel: options.channel,
    message: options.message,
    thread_ts: options.threadTs || null,
    upload_file: options.uploadFile !== false,
  });
  return response.data;
}

export async function sendToTeams(documentId, options) {
  const response = await api.post('/export/distribution/teams', {
    document_id: documentId,
    webhook_url: options.webhookUrl,
    title: options.title || null,
    message: options.message || null,
    mention_users: options.mentionUsers || [],
  });
  return response.data;
}

export async function sendWebhook(documentId, options) {
  const response = await api.post('/export/distribution/webhook', {
    document_id: documentId,
    webhook_url: options.webhookUrl,
    method: options.method || 'POST',
    headers: options.headers || {},
    include_content: options.includeContent !== false,
    payload_template: options.payloadTemplate || null,
  });
  return response.data;
}

export async function publishToPortal(documentId, options = {}) {
  const response = await api.post(`/export/distribution/portal/${documentId}`, {
    document_id: documentId,
    portal_path: options.portalPath || `/${documentId}`,
    title: options.title || null,
    description: options.description || null,
    tags: options.tags || [],
    public: options.public || false,
    password: options.password || null,
    expires_at: options.expiresAt || null,
  });
  return response.data;
}

// ============================================
// Embed
// ============================================

export async function generateEmbedToken(documentId, options = {}) {
  const response = await api.post(`/export/distribution/embed/${documentId}`, {
    document_id: documentId,
    width: options.width || 800,
    height: options.height || 600,
    allow_download: options.allowDownload || false,
    allow_print: options.allowPrint || false,
    show_toolbar: options.showToolbar !== false,
    theme: options.theme || 'light',
  });
  return response.data;
}

export async function revokeEmbedToken(tokenId) {
  const response = await api.delete(`/export/embed/${tokenId}`);
  return response.data;
}

export async function listEmbedTokens(documentId) {
  const response = await api.get(`/export/${documentId}/embed/tokens`);
  return asArray(response.data, ['tokens', 'embed_tokens', 'items', 'results']);
}

// ============================================
// Print
// ============================================

export async function printDocument(documentId, options = {}) {
  const response = await api.post(`/export/${documentId}/print`, {
    copies: options.copies || 1,
    printer: options.printer,
    duplex: options.duplex || false,
    color: options.color !== false,
  });
  return response.data;
}

export async function listPrinters() {
  const response = await api.get('/export/printers');
  return asArray(response.data, ['printers', 'items', 'results']);
}

// ============================================
// Export Jobs
// ============================================

export async function getExportJob(jobId) {
  const response = await api.get(`/export/jobs/${jobId}`);
  return response.data;
}

export async function listExportJobs(options = {}) {
  const response = await api.get('/export/jobs', {
    params: {
      status: options.status,
      limit: options.limit || 20,
    },
  });
  return asArray(response.data, ['jobs', 'exports', 'items', 'results']);
}

export async function cancelExportJob(jobId) {
  const response = await api.post(`/export/jobs/${jobId}/cancel`);
  return response.data;
}
