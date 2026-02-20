/**
 * Agents API Client
 * Handles AI agent operations (research, data analysis, email drafts, content, proofreading).
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
// Research Agent
// ============================================

export async function runResearchAgent(topic, options = {}) {
  const response = await api.post('/agents/research', {
    topic,
    depth: options.depth || 'comprehensive',
    focus_areas: options.focusAreas || null,
    max_sections: options.maxSections || 5,
  });
  return response.data;
}

// ============================================
// Data Analyst Agent
// ============================================

export async function runDataAnalystAgent(question, data, options = {}) {
  const response = await api.post('/agents/data-analysis', {
    question,
    data,
    data_description: options.dataDescription || null,
    generate_charts: options.generateCharts !== false,
  });
  return response.data;
}

// ============================================
// Email Draft Agent
// ============================================

export async function runEmailDraftAgent(context, purpose, options = {}) {
  const response = await api.post('/agents/email-draft', {
    context,
    purpose,
    tone: options.tone || 'professional',
    recipient_info: options.recipientInfo || null,
    previous_emails: options.previousEmails || null,
  });
  return response.data;
}

// ============================================
// Content Repurposing Agent
// ============================================

export async function runContentRepurposeAgent(content, sourceFormat, targetFormats, options = {}) {
  const response = await api.post('/agents/content-repurpose', {
    content,
    source_format: sourceFormat,
    target_formats: targetFormats,
    preserve_key_points: options.preserveKeyPoints !== false,
    adapt_length: options.adaptLength !== false,
  });
  return response.data;
}

// ============================================
// Proofreading Agent
// ============================================

export async function runProofreadingAgent(text, options = {}) {
  const response = await api.post('/agents/proofread', {
    text,
    style_guide: options.styleGuide || null,
    focus_areas: options.focusAreas || null,
    preserve_voice: options.preserveVoice !== false,
  });
  return response.data;
}

// ============================================
// Task Management
// ============================================

export async function getTask(taskId) {
  const response = await api.get(`/agents/tasks/${taskId}`);
  const payload = response.data;
  if (payload && typeof payload === 'object' && payload.task) {
    return payload.task;
  }
  return payload;
}

export async function listTasks(agentType = null) {
  const params = agentType ? { agent_type: agentType } : {};
  const response = await api.get('/agents/tasks', { params });
  return asArray(response.data, ['tasks', 'items', 'results']);
}

// ============================================
// Utility
// ============================================

export async function listAgentTypes() {
  const response = await api.get('/agents/types');
  const payload = response.data;
  if (Array.isArray(payload)) {
    return { types: payload };
  }
  if (payload && typeof payload === 'object') {
    return { ...payload, types: asArray(payload, ['types', 'items', 'results']) };
  }
  return { types: [] };
}

export async function listRepurposeFormats() {
  const response = await api.get('/agents/formats/repurpose');
  const payload = response.data;
  if (Array.isArray(payload)) {
    return { formats: payload };
  }
  if (payload && typeof payload === 'object') {
    return { ...payload, formats: asArray(payload, ['formats', 'items', 'results']) };
  }
  return { formats: [] };
}
